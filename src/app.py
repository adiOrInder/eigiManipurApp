from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.text import LabelBase
from kivy.core.window import Window
import requests

Window.clearcolor = (1,1,1,1)

LabelBase.register(
    name="Meetei",
    fn_regular="NotoSansMeeteiMayek-Medium.ttf"
)

SERVER = "http://127.0.0.1:8000/location"

LANG = {
    "en": {
        "title": "Need emergency?",
        "btn": "Emergency"
    },
    "mni": {
        "title": "ꯑꯦꯃꯔꯖꯦꯟꯁꯤ ꯑꯣꯏꯅꯥ?",
        "btn": "ꯑꯦꯃꯔꯖꯦꯟꯁꯤ"
    }
}

class MyRoot(BoxLayout):
    current_lang = "en"

    def switch_lang(self):
        self.current_lang = "mni" if self.current_lang == "en" else "en"

        self.ids.title.text = LANG[self.current_lang]["title"]
        self.ids.btn.text = LANG[self.current_lang]["btn"]

    def send_location(self, instance=None):
        self.show_emergency_options()

    def get_location(self):
        try:
            res = requests.get("https://ipinfo.io/json")
            data = res.json()
            lat, lon = data["loc"].split(",")
            return lat, lon
        except:
            return None, None

    def show_emergency_options(self):
        self.answers = {}

        box = BoxLayout(orientation="vertical", spacing=15)

        als = Button(text="ALS", font_size=28)
        bls = Button(text="BLS", font_size=28)

        als.bind(on_press=lambda x: self.next_step("level", "ALS"))
        bls.bind(on_press=lambda x: self.next_step("level", "BLS"))

        box.add_widget(als)
        box.add_widget(bls)

        self.popup = Popup(
            title="Select Service Type",
            content=box,
            size_hint=(0.8, 0.6)
        )
        self.popup.open()

    def next_step(self, key, value):
        self.answers[key] = value
        self.popup.dismiss()

        if key == "level":
            self.ask_yes_no("conscious", "Is patient conscious?")
        elif key == "conscious":
            self.ask_yes_no("trauma", "Any trauma?")
        elif key == "trauma":
            self.ask_yes_no("oxygen", "Needs oxygen support?")
        elif key == "oxygen":
            self.ask_age()

    def ask_yes_no(self, key, question):
        box = BoxLayout(orientation="vertical", spacing=15)

        yes = Button(text="YES", font_size=28)
        no = Button(text="NO", font_size=28)

        yes.bind(on_press=lambda x: self.handle_answer(key, "Yes"))
        no.bind(on_press=lambda x: self.handle_answer(key, "No"))

        box.add_widget(yes)
        box.add_widget(no)

        self.popup = Popup(
            title=question,
            content=box,
            size_hint=(0.8, 0.6)
        )
        self.popup.open()

    def handle_answer(self, key, value):
        self.answers[key] = value
        self.popup.dismiss()
        self.next_step(key, value)

    def ask_age(self):
        box = BoxLayout(orientation="vertical", spacing=15)

        self.age_input = TextInput(
            hint_text="Enter age",
            font_size=24,
            multiline=False
        )

        btn = Button(text="Submit", font_size=28)
        btn.bind(on_press=self.submit_all)

        box.add_widget(self.age_input)
        box.add_widget(btn)

        self.popup = Popup(
            title="Patient Age",
            content=box,
            size_hint=(0.8, 0.6)
        )
        self.popup.open()

    def submit_all(self, instance):
        self.answers["age"] = self.age_input.text

        lat, lon = self.get_location()

        print("DATA:", self.answers, lat, lon)

        try:
            requests.post(
                SERVER,
                json={
                    **self.answers,
                    "lat": lat,
                    "lon": lon
                }
            )
            print("Sent successfully")

        except Exception as e:
            print("Error:", e)

        self.popup.dismiss()

class iemeitei(App):
    def build(self):
        return MyRoot()

def main():
    iemeitei().run()

if __name__ == "__main__":
    main()
