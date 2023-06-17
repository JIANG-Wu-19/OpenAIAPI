import wx
import threading
import openai
import string
import pickle
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


class OpenAIAPIWrapper:
    def __init__(self, api_key):
        openai.api_key = api_key

    def classify_text(self, text):
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=text,
                max_tokens=100,
                temperature=0.5
            )
            classification = response.choices[0].text.strip()
            return classification
        except Exception as e:
            print(f"Error occurred during text classification: {e}")
            return None


def remove_punctuation(text):
    # 去除标点符号
    cleaned_text = text.translate(str.maketrans("", "", string.punctuation))
    return cleaned_text


def remove_stopwords(text):
    # 去除停用词
    stop_words = set(stopwords.words("english"))
    word_tokens = word_tokenize(text)
    filtered_text = [word for word in word_tokens if word.lower() not in stop_words]
    cleaned_text = " ".join(filtered_text)
    return cleaned_text


def extract_features(text):
    # 特征提取
    word_tokens = word_tokenize(text)
    features = {}
    for word in word_tokens:
        features[word] = features.get(word, 0) + 1
    return features


def process_step1(text):
    # 文本清洗
    cleaned_text = text.lower()  # 将文本转换为小写
    cleaned_text = remove_punctuation(cleaned_text)  # 去除标点符号
    cleaned_text = remove_stopwords(cleaned_text)  # 去除停用词

    return cleaned_text


def process_step2(text):
    # 特征提取
    features = extract_features(text)  # 提取文本特征

    print(features)
    feature_text = ""
    while len(features) != 0:
        key = max(features)
        feature_text = feature_text + key + ' '
        del features[key]
    return feature_text


class TextClassificationFrame(wx.Frame):
    def __init__(self):
        super(TextClassificationFrame, self).__init__(None, title="OpenAI Text Classification", size=(600, 400))
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.text_input = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        sizer.Add(self.text_input, 1, wx.EXPAND | wx.ALL, 5)

        self.result_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        sizer.Add(self.result_text, 1, wx.EXPAND | wx.ALL, 5)

        start_button = wx.Button(panel, label="Start Processing")
        start_button.Bind(wx.EVT_BUTTON, self.on_start_processing)
        sizer.Add(start_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        load_breakpoint_button = wx.Button(panel, label="Load Breakpoint")
        load_breakpoint_button.Bind(wx.EVT_BUTTON, self.on_load_breakpoint)
        sizer.Add(load_breakpoint_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        panel.SetSizer(sizer)

    def on_start_processing(self, event):
        self.result_text.Clear()
        text = self.text_input.GetValue()

        threading.Thread(target=self.process_text, args=(text,)).start()

    def process_text(self, text):
        # 使用链式思维处理文本
        # 第一步
        intermediate_text = process_step1(text)
        # 第二步
        intermediate_text = process_step2(intermediate_text)

        final_text = intermediate_text

        final_text = final_text + '''\nWhat is the sentiment of the above text,\
        give a list of emotions that the writer is expressing'''

        classification = api_wrapper.classify_text(final_text)
        if classification is not None:
            wx.CallAfter(self.result_text.AppendText, f"{classification}\n")

        breakpoint_data = {
            'text': text,
            'intermediate_text': intermediate_text,
            'final_text': final_text,
            'classification': classification,
        }
        with open('breakpoint_data.pkl', 'wb') as f:
            pickle.dump(breakpoint_data, f)

    def load_breakpoint_data(self, event=None):
        try:
            with open('breakpoint_data.pkl', 'rb') as f:
                breakpoint_data = pickle.load(f)
                text = breakpoint_data['text']
                intermediate_text = breakpoint_data['intermediate_text']
                final_text = breakpoint_data['final_text']
                Classfication=breakpoint_data['classification']

                self.text_input.SetValue(text)
                self.result_text.Clear()
                self.result_text.AppendText(Classfication)

        except FileNotFoundError:
            print("Breakpoint data not found.")

    def on_load_breakpoint(self, event):
        threading.Thread(target=self.load_breakpoint_data).start()


api_key = "MY_API_KEY"

api_wrapper = OpenAIAPIWrapper(api_key)

app = wx.App()
frame = TextClassificationFrame()
frame.Show()
app.MainLoop()
