class SyllableAnalyze:
    # 定義合法的音節組件
    INITIALS_TL = {'p', 'ph', 'm', 'b', 't', 'th', 'n', 'l', 'k', 'kh', 'ng', 'g', 'ts', 'tsh', 's', 'j', 'h'}
    INITIALS_POJ = {'p', 'ph', 'm', 'b', 't', 'th', 'n', 'l', 'k', 'kh', 'ng', 'g', 'ch', 'chh', 's', 'j', 'h'}
    VOWELS_TL = {'a', 'i', 'u', 'e', 'oo', 'o'}
    VOWELS_POJ = {'a', 'i', 'u', 'e', 'o͘', 'o'}
    CODAS = {'n','ng', 'm'}
    NASAL_MARKS = {'nn','ⁿ'}
    VOWELIZED_CONSONANTS = {'ng','m'}
    CHECKED_TONES = ('p','t','k','h')
    
    # 母音優先順序
    VOWEL_PRIORITY_TL = {'a':3,
                         'oo':1,
                         'e':1, 
                         'o':1, 
                         'i':0, 
                         'u':0}
    VOWEL_PRIORITY_POJ = {'o':4,
                          'o͘':4,
                          'e':3, 
                          'a':2, 
                          'u':1, 
                          'i':0}
    TONE_MARKS = {
        'a': {'2': 'á', '3': 'à', '5': 'â', '6': 'ǎ', '7': 'ā', '8': 'a̍'},
        'i': {'2': 'í', '3': 'ì', '5': 'î', '6': 'ǐ', '7': 'ī', '8': 'i̍'},
        'u': {'2': 'ú', '3': 'ù', '5': 'û', '6': 'ǔ', '7': 'ū', '8': 'u̍'},
        'e': {'2': 'é', '3': 'è', '5': 'ê', '6': 'ě', '7': 'ē', '8': 'e̍'},
        'oo': {'2': 'óo', '3': 'òo', '5': 'ôo', '6': 'ǒo', '7': 'ōo', '8': 'o̍o'},
        'o': {'2': 'ó', '3': 'ò', '5': 'ô', '6': 'ǒ', '7': 'ō', '8': 'o̍'},
        'ng': {'2': 'ńg', '3': 'ǹg', '5': 'n̂g', '6': 'ňg', '7': 'n̄g', '8': 'n̍g'},
        'm': {'2': 'ḿ', '3': 'm̀', '5': 'm̂', '6': 'm̌', '7': 'm̄', '8': 'm̍'},
        'o͘': {'2': 'ó͘', '3': 'ò͘', '5': 'ô͘', '6': 'ǒ͘', '7': 'ō͘', '8': 'o̍͘'}
    }
    

    def __init__(self, syllable: str, tone: str, is_poj=False):
        """
        初始化拼音音節處理器
        :param syllable: 拼音音節（不含聲調）
        :param tone: 聲調（1-4）
        """
        self.original :str = syllable
        self.tone :str = tone
        self.initial :str = '' #聲母
        self.final :str = '' #整個韻母
        self.vowels :str = '' #元音成分
        self.coda :str = '' #韻尾
        self.nasal :str = '' #鼻化成分
        self.main_vowel :str = ''
        self.checked :bool = False
        self.is_poj :bool = is_poj
        self.is_title :bool = False

    def parse(self):
        """解析音節結構"""
        # 檢查是否為空
        if not self.original:
            raise ValueError("音節不能為空")
        
        if self.original.istitle():
            self.is_title = True
            
        # 找出聲母
        current = self.original.lower()
        if self.is_poj:
            initial_list = self.INITIALS_POJ
        else:
            initial_list = self.INITIALS_TL

        if len(current) > 1: #音節長度 > 1 才有可能是聲母韻母的組合，否則聲母為零聲母
            for initial in sorted(initial_list, key=len, reverse=True):
                if current.startswith(initial):
                    self.initial = initial
                    current = current[len(initial):]
                    break
        if current == '':
            current = self.initial
            self.initial = ''

        self.final = current

        #確認入聲韻尾
        for tone in self.CHECKED_TONES:
            if current.endswith(tone): 
                self.checked = True
                self.coda = tone
                current = current[:-len(tone)]
                break
       
        for mark in self.NASAL_MARKS:
            if current.endswith(mark):
                self.nasal = mark
                current = current[:-len(mark)]
                break

        #確認陽聲韻
        for coda in sorted(self.CODAS,key=len,reverse=True):
            if current.endswith(coda) and len(self.coda) == 0:
                self.coda = coda
                current = current[:-len(coda)]
                break
            
        # #辨認鼻化標記是否被抓到韻尾，調整正確
        # for nasal_mark in self.NASAL_MARKS:
        #     if self.coda == nasal_mark:
        #         self.nasal = nasal_mark
        #         self.coda = ''
        #         break 
            
        self.vowels = current #此時元音部分應已確認
           
        # 檢查元音數量並處理元音化輔音的可能性
        if not 1 <= len(self.vowels) <= 3:
            for consonant in self.VOWELIZED_CONSONANTS:
                if self.coda == consonant:
                    self.vowels = consonant
                    self.coda = ''
                    break

        if len(self.vowels) ==0:
            if self.initial in self.VOWELIZED_CONSONANTS:
                self.vowels = self.initial
                self.initial = ''
                self.final = self.vowels+self.coda
            else:
                raise ValueError(f"母音數量必須在1-3個之間，目前有{len(self.vowels)}個")
            
        # 尋找主要母音
        self.main_vowel = self._find_main_vowel()
        
        return self
        
    def _find_main_vowel(self) -> str:
        """根據優先順序找出主要母音"""
        if not self.vowels:
            raise ValueError("沒有找到母音")
            
        # 根據優先順序表找出優先級最高的母音
        highest_priority = -1
        main_vowel = ''
        
        if self.vowels == 'oo':
            main_vowel = 'oo'
            return main_vowel
        elif self.vowels == 'o͘':
            main_vowel = 'o͘'
            return main_vowel
        
        if self.vowels in self.VOWELIZED_CONSONANTS:
            main_vowel = self.vowels
            return main_vowel

        vowels = list(self.vowels)

        if self.is_poj:
            priority_list = self.VOWEL_PRIORITY_POJ
        else:
            priority_list = self.VOWEL_PRIORITY_TL

        for vowel in vowels:
            priority = priority_list[vowel]
            if priority >= highest_priority: #後來者會替換前者
                highest_priority = priority
                main_vowel = vowel
                               
        return main_vowel
        
    def add_tone_mark(self) -> str:

        if not self.main_vowel or not self.tone:
            raise ValueError("缺少主要母音或聲調信息")
            
        if self.tone not in {'1', '2', '3','4', '5', '6', '7', '8'}:
            raise ValueError("聲調必須是1-8之間的數字")
            
        # 獲取帶聲調的母音
        if self.tone in {'1','4'}:
            toned_vowel = self.main_vowel # 1 4調不用調符
        else:
            toned_vowel = self.TONE_MARKS[self.main_vowel][self.tone]
        
        # 替換原始字符串中的主要母音
        result = self.original.replace(self.main_vowel, toned_vowel)

        return result
    
    def convert(self):
        if not self.is_poj:
            self.initial = self.initial.replace('ts','ch')
            self.final = self.final.replace('nn','ⁿ')
            self.nasal = self.nasal.replace('nn','ⁿ')
            
            if self.final in {'ing','ik'}:
                self.final = self.final.replace('i','e')
                self.vowels = 'e'
                self.main_vowel = 'e'
            
            if self.vowels == 'oo':
                self.final = self.final.replace('oo','o͘')
                self.vowels = 'o͘'
                self.main_vowel = 'o͘'
            if self.vowels in {'ua','ue'}:
                self.final = self.final.replace('u','o')
                self.vowels = self.vowels.replace('u','o')
                self.main_vowel = 'o'
            if self.vowels in {'iu','ui'}:
                self.main_vowel = 'u'
            
            self.original = self.initial+self.final

            if self.is_title:
                self.original = self.original.title()

            self.is_poj = True
        else:
            self.initial = self.initial.replace('ch','ts')
            self.final = self.final.replace('ⁿ','nn')
            self.nasal = self.nasal.replace('ⁿ','nn')
            
            if self.final in {'eng','ek'}:
                self.final = self.final.replace('e','i')
                self.vowels = 'i'
                self.main_vowel = 'i'
            
            if self.vowels == 'o͘':
                self.final = self.final.replace('o͘','oo')
                self.vowels = 'oo'
                self.main_vowel = 'oo'
            if self.vowels in {'oa','oe'}:
                self.final = self.final.replace('o','u')
                self.vowels = self.vowels.replace('o','u')
                if self.vowels == 'ua':
                    self.main_vowel = 'a'
                else:
                    self.main_vowel = 'e'
            if self.vowels == 'ui':
                self.main_vowel = 'i'
            
            self.original = self.initial+self.final

            if self.is_title:
                self.original = self.original.title()
            
            self.is_poj = False
            
        return self

            