import csv
import os
import re

"""
    lp2bw: This script outputs the CSV for Bitwarden import from information that can be obtained from the LastPassCLI.
    Copyright (C) 2022  rizenback000

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

# Reference:
# https://github.com/bitwarden/clients/blob/8aca6459cf2703284d675db410fe5aacaef44ee1/libs/common/src/importers/baseImporter.ts
usernameFieldNames = [
    'user',
    'name',
    'user name',
    'username',
    'login name',
    'email',
    'e-mail',
    'id',
    'userid',
    'user id',
    'login',
    'form_loginname',
    'wpname',
    'mail',
    'loginid',
    'login id',
    'log',
    'personlogin',
    'first name',
    'last name',
    'card#',
    'account #',
    'member',
    'member #']

passwordFieldNames = [
    'password',
    'pass word',
    'passphrase',
    'pass phrase',
    'pass',
    'code',
    'code word',
    'codeword',
    'secret',
    'secret word',
    'personpwd',
    'key',
    'keyword',
    'key word',
    'keyphrase',
    'key phrase',
    'form_pw',
    'wppassword',
    'pin',
    'pwd',
    'pw',
    'pword',
    'passwd',
    'p',
    'serial',
    'serial#',
    'license key',
    'reg #']


class LpInfo:
    def __init__(self, lp_item: list[str]):
        self.SiteName = ''
        self.Folder = ''
        self.Username = None
        self.Password = None
        self.URL = ''
        self.Notes = []
        self.Reprompt = 0
        self.Type = ''
        self.NoteType = None
        self.Favorite = 0
        self.Others = []
        lp_pattern = r'(.+) \[id: \d+\]'
        bw_pattern = r"(.+?):\s(.*)"
        result = ''
        note_type = False

        # 最初にType判別をするために全精査(もっとええ方法ないの？)
        # NoteTypeがあるものは確実にnoteだがURLがない
        # noteでもUsernameがあったり、Passwordがあったりする
        # URLがhttp://snはnote(多分secret note)
        for lp_line in lp_item:
            if lp_line.startswith('URL: http://sn'):
                self.Type = 'note'
                break
            if lp_line.startswith('NoteType: '):
                note_type = True
                self.Type = 'note'
                break

        if self.Type == '':
            self.Type = 'login'

        for lp_line in lp_item:
            if result == '':
                result = re.fullmatch(lp_pattern, lp_line)
                if result:
                    name: str = result.group(1)
                    # folder
                    if name.find('/') > 0:
                        spl = name.split('/')
                        self.Folder = spl[0]
                        self.SiteName = spl[1]
                    else:
                        self.SiteName = name
            else:
                result = re.fullmatch(bw_pattern, lp_line)
                # Notes以降はすべてノート扱いにする
                if len(self.Notes):
                    self.Notes.append(lp_line)
                elif result is not None:
                    key = result.group(1)
                    val = result.group(2).strip()

                    if self.Type == 'login' and self.Username is None and usernameFieldNames.count(key.lower()):
                        self.Username = val
                    elif self.Type == 'login' and self.Password is None and passwordFieldNames.count(key.lower()):
                        self.Password = val
                    elif key == 'URL':
                        self.URL = '' if self.Type == 'note' else val
                    elif key == 'Reprompt':
                        self.Reprompt = 1 if val == 'Yes' else 0
                    elif key == 'Notes':
                        self.Notes.append(val)
                    else:
                        # Boolean変換
                        if val == 'Checked':
                            val = 'true'
                        elif val == 'Unchecked':
                            val = 'false'

                        self.Others.append(key + ': ' + val)
                else:
                    # Notes以外かつヘッダありってそんなパターンあるんか？
                    print("例外パターン", lp_line)
                    return

        # NoteTypeが設定されているものはその他のフィールドはNotesになる
        if note_type:
            self.Notes = self.Others
            self.Others = []

        # favoriteはexportにしかでない。showには出ないし個人的に使ってないので0固定にする
        self.Favorite = 0
        return


def load_lp_file(path):
    f = open(path, 'r', encoding='UTF-8')
    text = f.read()
    f.close()
    return text


def siwake(text):
    lp_list = []
    lp_item = []
    for text_line in text.splitlines():
        # 区切り線までの行までを1件データとする。Notesの中に同じ文字列があるとバグる
        print(text_line)
        if text_line == '+=-_ +=-_+=-_+=-_+=-_+=-_+=-_+=-_+=-_+=-_':
            lp_list.append(LpInfo(lp_item))
            lp_item = []
        else:
            lp_item.append(text_line)

    return lp_list


# BitwardenのCSVヘッダ
# folder	favorite	type	name	notes	fields	reprompt	login_uri	login_username	login_password	login_totp
def lp_info_to_bit_csv(lp_path):
    lp_text = load_lp_file(lp_path)
    lp_list: list[LpInfo] = siwake(lp_text)

    with open('bitwarden_import(delete_this).csv', 'w', newline='', encoding='UTF-8') as f:
        writer = csv.writer(f)
        writer.writerow(
            ['folder', 'favorite', 'type', 'name', 'notes', 'fields', 'reprompt', 'login_uri', 'login_username',
             'login_password', 'login_totp'])

        for item in lp_list:
            notes = '\r\n'.join(item.Notes)
            fields = '\r\n'.join(item.Others)
            # TOTPはLastPassにない(たぶん)ので固定で0
            writer.writerow([item.Folder, item.Favorite, item.Type, item.SiteName, notes, fields, item.Reprompt,
                             item.URL, item.Username, item.Password, 0])
    return


if __name__ == '__main__':
    lp_info_to_bit_csv('lpass_show_file')
    os.remove('lpass_show_file')
