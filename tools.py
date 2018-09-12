import re

data = 'window.QRLogin.code = 200; window.QRLogin.uuid = "IaFEIY2ncA==";'

ret = re.findall('uuid = "(.*)";', data)[0]
#print(ret)


#text = '<error><ret>0</ret><message></message><skey>@crypt_7f94ab6d_09c6f5c641735b9d508b2973de7e1c73</skey><wxsid>dxtAt/oUed7drgJw</wxsid><wxuin>2150889942</wxuin><pass_ticket>DgAlY28j5CsCBMamz1h0FU42CAK6Bn%2BLk888LtaZnsOlckkPWFpgMu0KBFY91IUi</pass_ticket><isgrayscale>1</isgrayscale></error>'
from bs4 import BeautifulSoup

def xml_parse(text):
    result = {}
    soup = BeautifulSoup(text,'html.parser')
    tag_list = soup.find(name='error').find_all()
    for tag in tag_list:
       result[tag.name] = tag.text
    return result
v = '<error><ret>0</ret><message></message><skey>@crypt_7f94ab6d_09c6f5c641735b9d508b2973de7e1c73</skey><wxsid>dxtAt/oUed7drgJw</wxsid><wxuin>2150889942</wxuin><pass_ticket>DgAlY28j5CsCBMamz1h0FU42CAK6Bn%2BLk888LtaZnsOlckkPWFpgMu0KBFY91IUi</pass_ticket><isgrayscale>1</isgrayscale></error>'
result = xml_parse(v)
print(result)