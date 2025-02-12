from syllable_analyze import SyllableAnalyze
import re
import unicodedata

tone_marks:dict = {'0301':'2','0300':'3','0302':'5','030c':'6','0304':'7','030d':'8','030b':'9',
                   '2':'0301','3':'0300','5':'0302','6':'030c','7':'0304','8':'030d','9':'030b'}

class TaigiModes:
    # 台羅 -> 白話
    MODE_TL2POJ = 0
    # 白話字 -> 台羅
    MODE_POJ2TL = 1
    # 數字標 -> 符號標
    MODE_NO2DIAC = 2
    # 符號標 -> 數字標
    MODE_DIAC2NO = 3

def diacritic_removal(syllable:str) -> str:
    normalized = unicodedata.normalize('NFD',syllable)
    tone=''
    for idx, letter in enumerate(normalized):
        if unicodedata.category(letter) == 'Mn' and letter != '\u0358' :
            tone = tone_marks[format(ord(letter.lower()),'04x')]
            main_vowel = normalized[idx-1]
            main_vowel_idx = idx-1
    if tone:
        syllable = normalized[:main_vowel_idx]+main_vowel+normalized[main_vowel_idx+2:]
    else:
        if syllable.endswith(SyllableAnalyze.CHECKED_TONES):
            tone = '4'
        else:
            tone = '1'

    result = syllable+tone
    result = unicodedata.normalize("NFC",result)

    return result,syllable,tone

def sentence_process(sentence:str,mode:int):

    pattern = re.compile(r'[a-z0-9A-Zⁿo͘\u0301\u0300\u0302\u030c\u0304\u030d\u030b\-]+')
    target = unicodedata.normalize("NFD",sentence)

    words = pattern.findall(target)
    words = [item for sublist in words for item in sublist.split('-')]

    start=0
    end=0

    new = ''

    for word in words:
        end = target.find(word,start)
        new += target[start:end]

        match mode:
            case TaigiModes.MODE_TL2POJ:
                word_num = diacritic_removal(word)
                processed = SyllableAnalyze(word_num[1],word_num[2])
                processed.parse()
                processed.convert()
                processed = processed.add_tone_mark()
            case TaigiModes.MODE_POJ2TL:
                word_num = diacritic_removal(word)
                processed = SyllableAnalyze(word_num[1],word_num[2],True)
                processed.parse()
                processed.convert()
                processed = processed.add_tone_mark()
            case TaigiModes.MODE_NO2DIAC:
                processed = SyllableAnalyze(word[:-1],word[-1:])
                processed.parse()
                processed = processed.add_tone_mark()
            case TaigiModes.MODE_DIAC2NO:
                processed = diacritic_removal(word)[0]
        new += processed
        start = end+len(word)

    new+=target[start:]
    return new

class TaigiConverter:
    def __init__(self) -> None:
        self.mode: int = None
        self.text: str = None
    def update(self, text: str, mode: int) -> "TaigiConverter":
        self.text: str = text
        self.mode: int = mode
        return self

    @staticmethod
    def _convert_between_tl_and_poj(text: str,mode: int) -> str:
        # 請實作
        text = sentence_process(text,mode)
        return text
    
    @staticmethod
    def _convert_between_no_and_diacritics(text: str, mode: int) -> str:
        # 請實作
        text = sentence_process(text,mode)
            
        return text

    def convert(self) -> str:
        if 0 <= self.mode < 2:
            return self._convert_between_tl_and_poj(self.text,self.mode)
        if 2 <= self.mode < 4:
            return self._convert_between_no_and_diacritics(self.text, self.mode)
        raise ValueError("Unsupported Mode!")
    
if __name__ == '__main__':
    input_text: str = "gua2 si7 ong5-io1-tik4"
    taigi_converter = TaigiConverter()
    taigi_converter.update(input_text, TaigiModes.MODE_NO2DIAC)
    output_text: str = taigi_converter.convert()
    assert(output_text == "guá sī ông-io-tik")

    input_text: str = "guá sī ông-io-tik"
    taigi_converter = TaigiConverter()
    taigi_converter.update(input_text, TaigiModes.MODE_TL2POJ)
    output_text: str = taigi_converter.convert()
    assert(output_text == "góa sī ông-io-tek")