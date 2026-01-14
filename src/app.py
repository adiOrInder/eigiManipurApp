from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button
import requests
from kivy.core.text import LabelBase

LabelBase.register(
    name="Meetei",
    fn_regular="NotoSansMeeteiMayek-Medium.ttf"
)

SERVER = "http://127.0.0.1:8000/location"

LANG = {
    "en": {
        "welcome": "Welcome",
        "emergency": "Emergency",
        "heart": "Heart Problem",
        "preg": "Pregnancy",
        "injury": "Injury"
    },
    "mni": {
        "welcome": "ꯋꯦꯜꯀꯝ",
        "emergency": "ꯑꯦꯃꯔꯖꯦꯟꯁꯤ",
        "heart": "ꯍꯥꯔꯇ ꯄ꯭ꯔꯣꯕ꯭ꯂꯦꯝ",
        "preg": "ꯄ꯭ꯔꯦꯒꯅꯦꯟꯁꯤ",
        "injury": "ꯑꯤꯟꯖ꯭ꯔꯤ"
    }
}

class MyRoot(BoxLayout):
    current_lang = "en"

    def switch_lang(self):
        self.current_lang = "mni" if self.current_lang == "en" else "en"
        self.ids.title.text = LANG[self.current_lang]["welcome"]
        self.ids.btn.text = LANG[self.current_lang]["emergency"]

    def send_location(self, instance):
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
        box = BoxLayout(orientation="vertical", spacing=15)

        for key in ["heart", "preg", "injury"]:
            b = Button(
                text=LANG[self.current_lang][key],
                font_size=32
            )
            b.bind(on_press=self.handle_choice)
            box.add_widget(b)

        self.popup = Popup(
            title="Select Emergency",
            content=box,
            size_hint=(0.8, 0.6)
        )
        self.popup.open()
    #demo handle
    def handle_choice(self, btn):
        lat, lon = self.get_location()

        self.ids.random_la.text = (
            f"{btn.text}\nLat: {lat}\nLon: {lon}"
        )

        try:
            requests.post(
                SERVER,
                json={
                    "type": btn.text,
                    "lat": lat,
                    "lon": lon
                }
            )
            print("Sent:", btn.text, lat, lon)

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
