
import asyncio


class ProfanityChecker:
    def __init__(self):
        self.words = (
            'еблан', 'пиздеть', 'ебал', 'ссун', 'убивающему', 'убивающимся', 'пиздовать', 'залупа', 'убью',
            'заебенитесь',
            'убивающимися', 'ссаными', 'убивает', 'козел', 'пидорасина', 'хуила', 'ебана', 'ебанулась', 'хуякнулся',
            'хуякнем',
            'хуякнетесь', 'убивающие', 'подъеби', 'хуякнешь', 'ебанат', 'долбаеб', 'дрочила', 'говно', 'ебет',
            'блять', 'заебатый', 'мудачище', 'пиздуй', 'хуякнулась', 'тварь', 'пиздабол', 'гандон', 'наебали',
            'убивающемуся',
            'ссался', 'убивающегося', 'убивайте', 'подъебался', 'ебану', 'мудозвонка', 'педрило', 'подъебется',
            'пиздун',
            'убивающая', 'говнюк', 'убьется', 'пиздорванец', 'пиздить', 'заеби', 'мудачок', 'заебись', 'заебал',
            'ебаные',
            'гомик', 'ссаной', 'хуеплеты', 'хуево', 'убивающихся', 'хуякнише', 'заебала', 'урод', 'хуякнётесь', 'ссал',
            'убивающий', 'педераст', 'хуякнёте', 'гондон', 'ссите', 'хуева', 'подъебенитесь', 'хуйню', 'педрила',
            'подонок',
            'заебаться', 'пиздите', 'наеб', 'хуйло', 'ебнутый', 'ебошить', 'ссалась', 'пердак', 'блядина', 'ебать',
            'ссись',
            'хуякнемте', 'убивающиеся', 'хуярите', 'мудил', 'ебанулся', 'ссаного', 'мудило', 'ебнуть', 'ссали',
            'ебануть',
            'убивай', 'ссаться', 'хуякнуть', 'пиздит', 'хулиган', 'сучий', 'скотина', 'пиздор', 'падла', 'пиздануть',
            'ебало',
            'ссаных', 'пиздатые', 'наебал', 'наебнулась', 'подъебал', 'мудак', 'блядун', 'петух', 'убивающего',
            'блядунья',
            'сука', 'ссаный', 'дрочить', 'уродец', 'блядство', 'бляди', 'убивающе', 'мудозвон', 'убивающею', 'ебаться',
            'подъебаться', 'подъебанец', 'хуякнишь', 'ебля', 'пизда', 'пиздатый', 'ебаных', 'пиздатое', 'заеб',
            'убьются',
            'убивающийся', 'убивающемся', 'пиздануться', 'убьют', 'убивающим', 'тупица', 'пиздец', 'ебанутый',
            'пиздато',
            'пидар', 'ссаные', 'наебнул', 'ссаную', 'ебарь', 'пиздёж', 'говняный', 'ебанный', 'ебано', 'пердун',
            'убиваешь',
            'хуем', 'хуя', 'сучка', 'ссут', 'ебну', 'болван', 'убивать', 'убивающейся', 'ссала', 'хуев', 'кончина',
            'пизданутый', 'пидарас', 'ссыте', 'долбоебка', 'пиздобол', 'тупой', 'убивающаяся', 'пизд', 'пидарасина',
            'наебет',
            'ссаным', 'гнида', 'ебанул', 'ссутый', 'хуякни', 'поебень', 'убьешься', 'уебок', 'проститутка',
            'пидорас',
            'хуярит', 'пиздаболы', 'пиздоболы', 'ебливый', 'пизду', 'заебенила', 'пиздоваться', 'убивают', 'лошара',
            'хуиня',
            'пиздоватый', 'подъебись', 'наебнулся', 'хуеплетка', 'пизди', 'ебаный', 'параша', 'падонок', 'мудачина',
            'подъебало', 'ебло', 'пиздуйся', 'хуякните', 'убьешь', 'пизды', 'ссёт', 'педрилла', 'заебало', 'заебанец',
            'ссишь',
            'хули', 'мразь', 'сукин', 'пидор', 'убивающую', 'ебенок', 'еблище', 'подъебет', 'хуярить', 'педрилло',
            'хуйня',
            'убивающем', 'гомосек', 'ссаном', 'долбоеб', 'нахуй', 'ссытый', 'убиваю', 'ебучий', 'пиздюли', 'хуякнете',
            'хуепердун', 'пидарасы', 'убивающими', 'ссало', 'ублюдок', 'ссалка', 'убивающеся', 'муда', 'хуякать',
            'ебануться',
            'лох', 'подъебатый', 'мудила', 'хуякнёмте', 'шлюха', 'хуякнул', 'долбаёб', 'хуяк', 'ссышь', 'ссаная',
            'подъебка',
            'убиваете', 'убьет', 'убивающей', 'наебалась', 'заебалась', 'хуй', 'ебала', 'хуеплетпидор', 'подъебалась',
            'блядь',
            'ссыт', 'паршивец', 'ебан', 'дрянь', 'гомо', 'ссу', 'хуи', 'убиваются', 'конченный', 'ссаному', 'пиздишь',
            'убить',
            'заебался', 'пиздатая', 'ебашить', 'убиваем', 'подъебенила', 'мудачить', 'хуесос', 'хуеплет', 'сволочь',
            'хуякнет',
            'хуякнём', 'мразина', 'убивающих', 'ссёшь', 'проститут', 'заебется', 'наебать', 'пиздёнка', 'уродина',
            'пиздячить',
            'ссать', 'хуеплёт', 'хуеплет', 'выблядок' 'выблядище', 'шлюшка', 'шлюшенька', 'вагина', 'уёбище', 'блядь',
            'блядки', 'пидр', 'педик', 'бля', 'ахуели', 'опущенный'
        )
        self.similar_words = ('муха', 'жучка', 'гнида', 'коза', 'рыбка', 'гад', 'мартышка', 'балда', 'пуговка',
                              'тряпка', 'лошадка', 'велосипедик', 'олеговна', 'мда')

        self.d = {'а': ['а', 'a', '@'],
             'б': ['б', '6', 'b'],
             'в': ['в', 'b', 'v'],
             'г': ['г', 'r', 'g'],
             'д': ['д', 'd'],
             'е': ['е', 'e'],
             'ё': ['ё', 'e'],
             'ж': ['ж', 'zh', '*'],
             'з': ['з', '3', 'z'],
             'и': ['и', 'u', 'i', '*'],
             'й': ['й', 'u', 'i'],
             'к': ['к', 'k', 'i{', '|{'],
             'л': ['л', 'l', 'ji'],
             'м': ['м', 'm'],
             'н': ['н', 'h', 'n'],
             'о': ['о', 'o', '0', '*'],
             'п': ['п', 'n', 'p'],
             'р': ['р', 'r', 'p'],
             'с': ['с', 'c', 's'],
             'т': ['т', 'm', 't'],
             'у': ['у', 'y', 'u'],
             'ф': ['ф', 'f'],
             'х': ['х', 'x', 'h', '}{'],
             'ц': ['ц', 'c', 'u,'],
             'ч': ['ч', 'ch'],
             'ш': ['ш', 'sh'],
             'щ': ['щ', 'sch'],
             'ь': ['ь', 'b'],
             'ы': ['ы', 'bi'],
             'ъ': ['ъ'],
             'э': ['э', 'e'],
             'ю': ['ю', 'io'],
             'я': ['я', 'ya']
             }

    async def check(self, phrase):
        for key, value in self.d.items():
            for letter in value:
                phrase = phrase.replace(letter, key)

        for similar_word in self.similar_words:
            if similar_word in phrase:
                return None

        # Проходимся по всем словам.
        for word in self.words:
            # Разбиваем слово на части, и проходимся по ним.
            for part in range(len(phrase)):
                # Вот сам наш фрагмент.
                fragment = phrase[part: part + len(word)]
                # Если отличие этого фрагмента меньше или равно 25% этого слова, то считаем, что они равны.
                if self.distance(fragment, word) <= len(word) * 0.2:
                    # Если они равны, выводим надпись о их нахождении.
                    return True

    def distance(self, a, b):
        "Calculates the Levenshtein distance between a and b."
        n, m = len(a), len(b)
        if n > m:
            # Make sure n <= m, to use O(min(n, m)) space
            a, b = b, a
            n, m = m, n

        current_row = range(n + 1)  # Keep current and previous row, not entire matrix
        for i in range(1, m + 1):
            previous_row, current_row = current_row, [i] + [0] * n
            for j in range(1, n + 1):
                add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
                if a[j - 1] != b[i - 1]:
                    change += 1
                current_row[j] = min(add, delete, change)

        return current_row[n]

