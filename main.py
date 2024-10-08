import csv
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
from xml.dom import minidom
import xml.etree.ElementTree as ET
import os
import requests

def prettify(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    # print(reparsed.toprettyxml(indent="    "))
    return reparsed.toprettyxml(indent="    ")


def download_audio(url, save_path, file_name):
    try:
        # Send a GET request to the URL
        response = requests.get(url, stream=True)
        # Check if the request was successful
        if response.status_code == 200:
            # Create the full file path
            file_path = os.path.join(save_path, file_name)
            # Write the content to the file
            with open(file_path, 'wb') as audio_file:
                for chunk in response.iter_content(chunk_size=1024):
                    audio_file.write(chunk)
            print(f"Downloaded: {file_name}")
        else:
            print(f"Failed to download {file_name}: Status code {response.status_code}")
    except Exception as e:
        print(f"Error downloading {file_name}: {e}")


def create_xml(curr_ePark, out_ePark, file, dialect, lang, lang_code, dir, ePark):

    if file != "05 恆春阿美語.csv" or dir != "文化篇":
        return
    xml_output = os.path.join(out_ePark, lang)
    audio_output = os.path.join(xml_output, "audio")
    
    if not os.path.exists(xml_output):
        os.mkdir(xml_output)

    if not os.path.exists(audio_output):
        os.mkdir(audio_output)

    root = Element("TEXT")
    root.set("id", "")
    root.set("xml:lang", lang_code)
    root.set("source", ePark + " " + dir + " " + dialect)
    root.set("citation", "")
    root.set("copyright", "")

    with open(os.path.join(curr_ePark, file), mode='r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row_id, row in enumerate(reader):
            form_sentence, chinese_translation = row[:2]
            english_translation = ""
            audio_url = row[-1]
            if len(row)>3:
                form_sentence, english_translation, chinese_translation = row[:3]
            s_element = SubElement(root, "S")
            s_element.set("id", str(row_id))
            
            form_element = SubElement(s_element, "FORM")
            form_element.text = form_sentence

            transl_element = SubElement(s_element, "TRANSL")
            transl_element.set("xml:lang", "zh")
            transl_element.text = chinese_translation
            if english_translation!="":
                transl_element = SubElement(s_element, "TRANSL")
                transl_element.set("xml:lang", "en")
                transl_element.text = english_translation
            
            audio_file = dir+"_"+dialect+"_"+str(row_id)+audio_url.split(".")[-1]
            download_audio(audio_url, audio_output, audio_file)
            audio_element = SubElement(s_element, "AUDIO")
            audio_element.set("file", audio_file)
            audio_element.set("url", audio_url)


    try:
        xml_string = prettify(root)
    except:
        xml_string = ""
        print(ePark, dir, dialect, lang, file)

    with open(os.path.join(xml_output, dialect+".xml"), "w", encoding="utf-8") as xmlfile:
        xmlfile.write(xml_string)
    
    




def ePark1_2(dialects, lang_codes, ePark_ver):
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(curr_dir, "output")
    for dir in os.listdir(os.path.join(curr_dir, ePark_ver)):
        if dir.startswith('.'):
            continue

        curr_ePark = os.path.join(curr_dir, ePark_ver, dir)
        out_ePark = os.path.join(output_dir, dir)

        if not os.path.exists(out_ePark):
            os.mkdir(out_ePark)
        
        for file in os.listdir(curr_ePark):
            idx = file.split(" ")[0]
            if not idx.isdigit():
                continue

            lang = dialects[idx].split("_")[-1]
            lang_code = lang_codes[lang]
            if ePark_ver == "ePark_1":
                create_xml(curr_ePark, out_ePark, file, dialects[idx], lang, lang_code, dir, "ePark1")
            else:
                create_xml(curr_ePark, out_ePark, file, dialects[idx], lang, lang_code, dir, "ePark2")





def main():
    dialects = dict()
    lang_codes = {"Amis":"ami", "Atayal":"tay", "Saisiyat":"xsy", "Thao":"ssf", "Seediq":"trv", "Bunun":"bnn", 
                  "Paiwan":"pwn", "Rukai":"dru", "Truku":"trv", "Kavalan":"ckv", "Tsou":"tsu", "Kanakanavu":"xnb", 
                  "Saaroa":"sxr", "Puyuma":"pyu", "Yami":"tao", "Sakizaya":"szy"}
    with open("dialects.csv", mode='r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        for _, row in enumerate(reader):
            dialects[row[0]] = row[1]
    #ePark1_2(dialects, lang_codes, "ePark_1")
    ePark1_2(dialects, lang_codes, "ePark_2")
    

if __name__ == "__main__":
    main()


