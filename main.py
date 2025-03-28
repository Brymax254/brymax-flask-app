from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.webview import WebView  # Use kivy_garden's WebView


class WebApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create a WebView widget
        self.webview = WebView()
        self.webview.url = "http://127.0.0.1:5000"  # Flask App URL

        # Inject JavaScript to add CSRF token
        self.webview.bind(on_load=self.inject_csrf_token)

        self.add_widget(self.webview)

    def inject_csrf_token(self, instance):
        """Inject CSRF token into all requests made from the WebView."""
        js_code = """
        document.cookie = "X-CSRFToken=" + document.querySelector('meta[name="csrf-token"]').getAttribute("content");
        """
        self.webview.eval_js(js_code)  # Execute JavaScript inside WebView


class MyApp(App):
    def build(self):
        return WebApp()


if __name__ == "__main__":
    MyApp().run()
