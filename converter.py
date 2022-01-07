import demoji
import pandas as pd
import requests

C_TOKEN = '***REMOVED***'
C_LINK = 'https://free.currconv.com/api/v7/'

api_dict = list(requests.get('{}countries?apiKey={}'.format(C_LINK, C_TOKEN)).json().values())[0]
df = pd.DataFrame.from_dict(api_dict, orient='index')


# Gives list of country names for string with flag emojis
def emoji_to_country_name(string):
    return [x[6:] for x in list(demoji.findall(string).values())][0]


# Gives ISO-4217 currency code for country name or ISO-3166 alpha-2/alpha-3 country code
def name_to_cur_id(string):
    if not string[0].isalpha():                             # emoji flag
        if string == '🇪🇺':                                  # API lacks exact EU info
            return 'EUR'
        if string in '🏴󠁧󠁢󠁥󠁮󠁧󠁿 🏴󠁧󠁢󠁳󠁣󠁴󠁿 🏴󠁧󠁢󠁷󠁬󠁳󠁿' and string != '🏴':         # UK parts + check for black flag
            return 'GBP'
        string = emoji_to_country_name(string)
        return df[df['name'] == string]['currencyId'][0]
    elif len(string) == 2:                                  # ISO3166 alpha-2 code
        if string == 'EU':                                  # API lacks exact EU info
            return 'EUR'
        return df.loc[string]['currencyId']
    elif len(string) == 3:
        return df[df['alpha3'] == string]['currencyId'][0]  # ISO3166 alpha-3 code
    else:
        return df[df['name'] == string]['currencyId'][0]    # country name


def convert(num, src, dst):
    num = abs(round(float(num), 2))
    if src not in list(df['currencyId']):
        src = name_to_cur_id(src)
    if dst not in list(df['currencyId']):
        dst = name_to_cur_id(dst)
    res = round(num * list(requests.get('{}convert?q={}_{}&compact=ultra&apiKey={}'.format(C_LINK, src, dst, C_TOKEN)).json().values())[0], 2)
    return "{} {} = {} {}".format('{:,}'.format(num), src, '{:,}'.format(res), dst)
