from os import path

from chrome_extension import Extension


class CaptchaSolver(Extension):
    def __init__(self, api_key: str, download_dir: str, enable_plugin_manually):
        super().__init__(
            extension_id="ifibfemgeogfhoebkmokieepdoobkbpo",
            extension_name="2captcha",
            download_dir=download_dir,
            api_key=api_key,
        )

        self.enable_plugin_manually = enable_plugin_manually

    def update_files(self, api_key):
        def disable_plugin(content):
            key_replaced = content.replace(
                "isPluginEnabled: true,", "isPluginEnabled: false,"
            )
            return key_replaced

        def update_captcha_solution(content):
            key_replaced = content.replace(
                "recaptchaV2Type: 'token',", "recaptchaV2Type: 'click',"
            )
            return key_replaced

        def update_api_key(content):
            key_replaced = content.replace("apiKey: null,", f'apiKey: "{api_key}",')
            return key_replaced

        self.get_file(path.join("common", "config.js")).update_contents(
            update_captcha_solution
        )

        if self.enable_plugin_manually:
            self.get_file(path.join("common", "config.js")).update_contents(
                disable_plugin
            )

        self.get_file(path.join("common", "config.js")).update_contents(update_api_key)
