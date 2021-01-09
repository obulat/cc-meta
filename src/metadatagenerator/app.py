"""
Save your CC-licensed work metadata as a qr code or xmp file
"""
import os
import qrcode
from jinja2 import Template

from typing import Dict

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER



xmp_template = """{%- set COPYRIGHTED = 'CC0' not in license -%}
<?xpacket begin='' id='W5M0MpCehiHzreSzNTczkc9d'?>
<x:xmpmeta xmlns:x='adobe:ns:meta/'>
    <rdf:RDF 
        xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'
        xmlns:xapRights='http://ns.adobe.com/xap/1.0/rights/'
        xmlns:cc='http://creativecommons.org/ns#'
        {%- if title_of_work -%}
        xmlns:dc='http://purl.org/dc/elements/1.1/
        {%- endif -%}
        >
        <rdf:Description rdf:about=''>
            <xapRights:Marked>{{'True' if COPYRIGHTED else 'False'}}</xapRights:Marked>
            {% if creator_of_work %}
            <xapRights:Owner>
                <rdf:Bag>
                    <rdf:li>{{ creator_of_work }}</rdf:li>
                </rdf:Bag>
            </xapRights:Owner>
            {%- endif -%}
            {%- if COPYRIGHTED and link_to_work-%}
            <xapRights:WebStatement rdf:resource='{{link_to_work}}'/>
            {%- endif -%}
            <xapRights:UsageTerms>
                <rdf:Alt>
                    <rdf:li xml:lang='x-default'>This work is licensed under &lt;a href=&#34;{{license_url}}&#34;&gt;{{license_full}}&lt;/a&gt;</rdf:li>
                    <rdf:li xml:lang='{{lang}}'>This work is licensed under &lt;a href=&#34;{{license_url}}&#34;&gt;{{license_full}}&lt;/a&gt;</rdf:li>
                </rdf:Alt>
            </xapRights:UsageTerms>
            <cc:license rdf:resource='{{ license_url }}'/>
            {%- if creator_of_work -%}
                <cc:attributionName>{{creator_of_work}}</cc:attributionName>
            {% endif %}
            <dc:title>
                <rdf:Alt>
                    <rdf:li xml:lang='x-default'>{{ title_of_work }}</rdf:li>
                    <rdf:li xml:lang='{{lang}}'>{{ title_of_work }}</rdf:li>
                </rdf:Alt>
            </dc:title>
        </rdf:Description>
</rdf:RDF>
</x:xmpmeta>
<?xpacket end='r'?>
"""
LICENSES = {
    'CC0 1.0': {
        'FULL': 'CC0 1.0 Universal',
        'URL': 'http://creativecommons.org/publicdomain/zero/1.0/',
        'ICONS': ['cc', 'zero']
    },
    'CC BY 4.0': {
        'FULL': 'Attribution 4.0 International',
        'URL': 'http://creativecommons.org/licenses/by/4.0/',
        'ICONS': ['cc', 'by']
    },
    'CC BY-SA 4.0': {
        'FULL': 'Attribution-ShareAlike 4.0 International',
        'URL': 'http://creativecommons.org/licenses/by-sa/4.0/',
        'ICONS': ['cc', 'by', 'sa']
    },
    'CC BY-NC 4.0': {
        'FULL': 'Attribution-NonCommercial 4.0 International',
        'URL': 'http://creativecommons.org/licenses/by-nc/4.0/',
        'ICONS': ['cc', 'by', 'nc']
    },
    'CC BY-NC-SA 4.0': {
        'FULL': 'Attribution-NonCommercial-ShareAlike 4.0 International',
        'URL': 'http://creativecommons.org/licenses/by-nc-sa/4.0/',
        'ICONS': ['cc', 'by', 'nc', 'sa']
    },
    'CC BY-NC-ND 4.0': {
        'FULL': 'Attribution-NonCommercial-NoDerivatives 4.0 International',
        'URL': 'http://creativecommons.org/licenses/by-nc-nd/4.0/',
        'ICONS': ['cc', 'by', 'nc', 'nd']
    },
    'CC BY-ND 4.0': {
        'FULL': 'Attribution-NoDerivatives 4.0 International',
        'URL': 'http://creativecommons.org/licenses/by-nd/4.0/',
        'ICONS': ['cc', 'by', 'nd']
    }
}

class SelectedLicense:
    def __init__(self):
        self.license = 'CC0 1.0'
        self.title_of_work = ''
        self.creator_of_work = ''
        self.link_to_work = ''
        self.link_to_creator_profile = ''
        self._qr = None

    def creator_html(self):
        if not self.creator_of_work:
            return ''
        if self.link_to_creator_profile:
            creator = f'by <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="{self.link_to_creator_profile}">{self.creator_of_work}</a>'
        else:
            creator = f'by <span property="cc:attributionName">{self.creator_of_work}</span>'
        return creator

    def work_html(self):
        if not self.title_of_work:
            return "This work"
        if self.link_to_work:
            workCode = f'<a rel="cc:attributionURL" property="dct:title" href="{self.link_to_work}">{self.title_of_work}</a>'
        else:
            workCode = f'<span property="dct:title">{self.title_of_work}</span>'
        return workCode
    
    def update(self, data: Dict):
        """ Update selected license data:
        """
        self.__setattr__(data['id'], data['value'])
    
    @property
    def html(self):
        if not self.license:
            return ''
        return f"{self.work_html()}{self.creator_html()} is licensed under {self.license}. To view a copy of this license, visit {LICENSES[self.license]['URL']}"
    
    def generate_xmp(self):
        template = Template(xmp_template)
        return template.render(
            license=self.license,
            license_full=LICENSES[self.license]['FULL'],
            title_of_work=self.title_of_work,
            creator_of_work=self.creator_of_work,
            link_to_work=self.link_to_work,
            link_to_creator_profile=self.link_to_creator_profile,
            license_url=LICENSES[self.license]['URL'] if self.license else '',
            lang="en-US"
        )

    @property
    def xmp(self):
        return self.generate_xmp()

    @property
    def qr(self):
        return self.generate_qr_code()
    
    def generate_qr_code(self):
        return qrcode.make(self.html)


class MetadataGenerator(toga.App):

  
    def details_form(self):
        license_chooser_label = toga.Label(
            text="Choose your CC license:",
            style=Pack(padding_bottom=5)
            )
        self.license_chooser = toga.widgets.selection.Selection(
            id='license',
            on_select=self.on_input_change,
            items=['CC0 1.0', 'CC BY 4.0', 'CC BY-NC 4.0', 'CC BY-ND 4.0', 'CC BY-SA 4.0', 'CC BY-NC-ND 4.0', 'CC BY-NC-SA 4.0']
            )
        license = toga.Box(
            children=[license_chooser_label, self.license_chooser],
            style=Pack(direction=COLUMN, padding_bottom=20)
            )
        details_data = [
            {
                'label': 'Title of work',
                'placeholder': 'The title of your work',
                'id': 'title_of_work'
            },
            {
                'label': 'Creator of work',
                'placeholder': 'Jane Doe',
                'id': 'creator'
            },
            {
                'label': 'Link to work',
                'placeholder': 'https://janedoe.com/image.jpg',
                'id': 'link_to_work'
            },
            {
                'label': 'Link to Creator Profile',
                'placeholder': 'https://janedoe.com',
                'id': 'link_to_creator_profile'
            }
        ]
        fields = [license]
        for detail in details_data:
            label = toga.Label(text=detail['label'], style=Pack(padding_bottom=5))
            input = toga.widgets.textinput.TextInput(
                placeholder=detail['placeholder'],
                id=detail['id'],
                on_change=self.on_input_change,
                on_lose_focus=self.on_input_blur
            )
            field = toga.Box(
                children=[label, input],
                style=Pack(direction=COLUMN, padding_bottom=20)
                )
            fields.append(field)

        details_form = toga.Box(
            style=Pack(direction=COLUMN),
            children=fields
            )
        return details_form
    
    @property
    def qr_temp_filename(self):
        dirpath = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(dirpath, 'resources', f'temp.png')

    def update_license_text(self):
        self.license_text.text = "Your selected license: " + self.license_data.html
        self.attribution_text.value = self.license_data.html
        

    def on_input_change(self, widget):
        self.license_data.update({'id': widget.id, 'value': widget.value})
        self.update_license_text()
        self.update_xmp()
        if widget.id == 'license':
            self.update_qr()

    def on_input_blur(self, widget):
        self.update_qr()

    def update_xmp(self):
        self.xmp_text.value = self.license_data.xmp

    def update_qr(self):
        if self.qr_image._impl.native.Image is not None:
            self.qr_image._impl.native.Image.Dispose()
        if os.path.isfile(self.qr_temp_filename):
            os.remove(self.qr_temp_filename)
        try:
            with open(self.qr_temp_filename, 'wb+') as temp:
                qr = self.license_data.qr
                qr._img.save(temp, 'png')
        except Exception as e:
            print(f"Cannot update the qr code due to {e}")
        qr_toga_image = toga.Image(self.qr_temp_filename)
        self.qr_image.image = qr_toga_image

    def save_qr(self, widget):
        fname = self.license_data.license + '.png'
        try:
            save_path = self.main_window.save_file_dialog(
                "Save file with Toga",
                suggested_filename=fname)
            if save_path is not None:
                qr = self.license_data.generate_qr_code()
                with open(save_path, 'wb+') as temp:
                    qr._img.save(temp, 'png')
                print("File saved with Toga:" + save_path)
        except ValueError:
            print("Dialog was closed")
            
    def save_xmp(self, widget):
        fname = self.license_data.license + '.xmp'
        try:
            save_path = self.main_window.save_file_dialog(
                "Save file with Toga",
                suggested_filename=fname)
            if save_path is not None:
                with open(save_path, 'w+') as temp:
                    temp.write(self.license_data.xmp)
                print("File saved with Toga:" + save_path)
        except ValueError:
            print("Dialog was closed")
    
    def results_pane(self):
        results_pane = toga.OptionContainer(style=Pack(width=280, padding_left=20))

        self.qr_image = toga.ImageView(id='qr', image=None, style=Pack(width=250, height=250, padding_bottom=10))
        
        self.save_qr_button = toga.Button('Save QR', on_press=self.save_qr ,style=Pack(alignment=CENTER, width=250))

        self.qr_box = toga.Box(
            children=[self.qr_image, self.save_qr_button],
            style=Pack(direction=COLUMN, padding=10, width=270)
            )
        results_pane.add('QR Code', self.qr_box)

        self.xmp_text = toga.MultilineTextInput(
            style=Pack(width=270, height=350, padding=5)
            )
        self.xmp_button = toga.Button(
            'Save XMP',
            on_press=self.save_xmp,
            style=Pack(width=250, alignment=CENTER)
            )
        self.xmp_box = toga.Box(
            children=[self.xmp_text, self.xmp_button],
            style=Pack(direction=COLUMN)
        )
        results_pane.add('XMP', self.xmp_box)
        return results_pane
    
    def attribution_pane(self):
        self.license_text = toga.Label(text="Your selected license")
        self.attribution_text = toga.MultilineTextInput(
            initial="No license selected",
            readonly=True,
            style=Pack(height=40, padding_top=10)
            )

        return toga.Box(
            children=[self.license_text, self.attribution_text],
            style=Pack(direction=COLUMN, padding=10)
            )

    def startup(self):
        """
        Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        self.license_data = SelectedLicense()

        self.main_window = toga.MainWindow(title=self.formal_name)

        self.top_container = toga.SplitContainer(
            direction=toga.SplitContainer.VERTICAL,
            style=Pack(height=320)
            )


        self.outer_container = toga.Box(
            children=[self.top_container, self.attribution_pane()],
            style=Pack(direction=COLUMN, padding=20)
            )

        self.top_container.content = [self.details_form(), self.results_pane()]

        self.main_window.content = self.outer_container
        self.main_window.show()


def main():
    return MetadataGenerator()
