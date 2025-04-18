import requests
import json


class Translator:
    """Using reverse-engineering to call Translate API"""

    def __init__(self):
        self.session = requests.session()
        self.session.headers[
            "User-Agent"
        ] = "Mozilla/5.0 (X11; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0"
        self.session.headers[
            "Content-Type"
        ] = "application/x-www-form-urlencoded;charset=utf-8"
        self.url = "https://translate.google.com/_/TranslateWebserverUi/data/batchexecute?rpcids=MkEWBc"

    def translate(self, text, dest="en", src="auto"):
        data = self._build_data_post(text, dest, src)
        response = self.session.post(self.url, data)
        return self._read_response(response)

    def _build_data_post(self, text, dest, src):
        return {
            "f.req": json.dumps(
                [
                    [
                        [
                            "MkEWBc",
                            f'[["{text}", "{src}", "{dest}", true], [null]]',
                            None,
                            "generic",
                        ]
                    ]
                ]
            )
        }

    def _read_response(self, response):
        translation = Translation("<TRANSLATION ERROR>")
        try:
            content = response.text
            start_blob = content.find("[[")
            blob = json.loads(content[start_blob:])

            temp_result = json.loads(blob[0][2])
            translation.text = temp_result[1][0][0][5][0][0]
        except Exception as e:
            print(e)
            print(content)
        finally:
            return translation


class Translation:
    def __init__(self, text):
        self.text = text
