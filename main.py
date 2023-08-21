from bs4 import BeautifulSoup
import requests
import time
temp = ""
code=""
output = '''<?xml version="1.0" encoding="UTF-8"?>
<iXDOC format="variable" min="0" max="1" subChar=":" dataChar="+" numChar="." relChar="?" repChar=" " segChar="\\n or '" emptyEnd="true" lastEnd="false" optionChar="\\n\\r">
	<UNA format="fixed" length="9" optionChar="\\r\\n" min="0" max="1" errorLevel="true">
		<TAG format="fixed" key="true" length="3" min="1">UNA</TAG>
		<SubChar format="fixed" setAttribute="subChar" length="1"/>
		<DataChar format="fixed" setAttribute="dataChar" length="1"/>
		<NumChar format="fixed" setAttribute="numChar" length="1"/>
		<RelChar format="fixed" setAttribute="relChar" length="1"/>
		<RepChar format="fixed" setAttribute="repChar" length="1"/>
		<SegChar format="fixed" setAttribute="segChar" length="1" trim="false" optionChar="\\r\\n"/>
	</UNA>
	<UNB end="$segChar" lastEnd="true" emptyEnd="false" min="1" max="1" optionChar="\\r\\n" errorLevel="true">
		<TAG end="$dataChar" min="1" key="true">UNB</TAG>
		<S001 end="$dataChar" min="1">
			<D0001 end="$subChar" min="1" minSize="4" maxSize="4"/>
			<D0002 end="$subChar" min="1" minSize="1" maxSize="1"/>
			<D0080 end="$subChar" min="0" maxSize="6"/>
			<D0133 end="$subChar" min="0" maxSize="3"/>
		</S001>
		<S002 end="$dataChar" min="1">
			<D0004 end="$subChar" min="1" maxSize="35"/>
			<D0007 end="$subChar" min="0" maxSize="4"/>
			<D0008 end="$subChar" min="0" maxSize="35"/>
			<D0042 end="$subChar" min="0" maxSize="35"/>
		</S002>
		<S003 end="$dataChar" min="1">
			<D0010 end="$subChar" min="1" maxSize="35"/>
			<D0007 end="$subChar" min="0" maxSize="4"/>
			<D0014 end="$subChar" min="0" maxSize="35"/>
			<D0046 end="$subChar" min="0" maxSize="35"/>
		</S003>
		<S004 end="$dataChar" min="1">
			<D0017 end="$subChar" min="1" minSize="6" maxSize="6" numeric="true"/>
			<D0019 end="$subChar" min="1" minSize="4" maxSize="4" numeric="true"/>
		</S004>
		<D0020 end="$dataChar" min="1" maxSize="14"/>
		<S0005 end="$dataChar">
			<D0022 end="$subChar" min="1" maxSize="14"/>
			<D0025 end="$subChar" min="0" minSize="2" maxSize="2"/>
		</S0005>
		<D0026 end="$dataChar" maxSize="14"/>
		<D0029 end="$dataChar" minSize="1" maxSize="1"/>
		<D0031 end="$dataChar" minSize="1" maxSize="1" numeric="true"/>
		<D0032 end="$dataChar" maxSize="35"/>
		<D0035 end="$dataChar" minSize="1" maxSize="1" numeric="true"/>
	</UNB>'''

#to calculate runtime
def my_function():
    total = 0
    for i in range(1000000):
        total += i
start_time = time.time()
#delete "." and ".." in the html input code
def delete_elements(string):
    if ".." in string:
        return string[3:]
    elif "." in string:
        return string[2:]
    else:
        return string


#main function where I create my main tags
def class_name(name):
    #global variable
    #output:add line by line output
    #Temp :variable I use to control where the tags end
    global output,temp
    try:
        innerClassName = name["class"]
        if innerClassName == ['elm', 'e', 'edi']:
            code = name.contents[0].contents[0]
            # Extracting the attributes for min, max, and mandatory
            attributes = name.contents[2].find_all('span')
            max_size = delete_elements(attributes[2].text.strip())
            is_mandatory = "Mandatory" in attributes[0].text.strip()
            #If mandatory is true, the tag's minimum size should be 1, otherwise it should be 0
            if is_mandatory:
                min_value = "1"
            else:
                min_value = "0"
            output += f"<D{code} end=\"$dataChar\" min=\"{min_value}\" maxSize=\"{max_size}\"/>\n"
        elif innerClassName == ['com', 'elm']:
            code = name.contents[0].contents[0]
            temp=code
            is_mandatory = "Mandatory" in name.contents[2].text.strip()
            if is_mandatory:
                min_value = "1"
            else:
                min_value = "0"
            output += f"<{code} end=\"$dataChar\" min=\"{min_value}\">\n"
    except Exception as e:
        for i in name:
            code = i.contents[0].contents[0]
            is_mandatory = "Mandatory" in i.contents[2].text.strip()
            attributes = i.contents[2].find_all('span')
            max_size = delete_elements(attributes[2].text.strip())
            if is_mandatory:
                min_value = "1"
            else:
                min_value = "0"
            output += f"<D{code} end=\"$subChar\" min=\"{min_value}\" maxSize=\"{max_size}\"/>\n"
        if temp!="":
            output += "\t</"  + temp.string + ">\n"

#This function is the function i use control containing groop loop tags
#This function is recursive because group loops can contain group loops.
def group_loop(name, spaceCount):
    global output,code,temp
    isGroup = False
    if (name.contents[1].contents[0].text.strip()[:3] == "GRP"):
        code = "Group" + name.contents[1].contents[0].text.strip()[3:]+"_Loop"
        isGroup = True
        temp=code
    try:
        innerClassName = name["class"]
        if (name.contents[1].contents[0].text.strip()[:3] != "GRP"):
            code = name.contents[1].contents[0].text.strip()
        attributes = name.contents[3].find_all('span')
        max_size = attributes[0].text.strip()
        is_mandatory = "Mandatory" in attributes[1].text.strip()
        if is_mandatory:
            min_value = "1"
        else:
            min_value = "0"
        if (name.contents[1].contents[0].text.strip()[:3] == "GRP"):
            output += f"<{code} min=\"0\""
            output += f" max=\"{max_size}\" format=\"none\">\n"
        else:
            output += f"<{code} end=\"$segChar\" lastEnd=\"true\" emptyEnd=\"false\"min=\"{min_value}\"max=\"{max_size}\"optionChar=\"\\r\\n\" errorLevel=\"true\">\n"
            output += f"<TAG end=\"$dataChar\" key=\"true\" min=\"1\">{code}</TAG>\n"
            for i in name.contents[3].contents[1].contents:
                if i != '\n' and i != ' ':
                    class_name(i)
            output+=f"</{code}>\n"
        if innerClassName == ['aggr', 'grp', 'edi']:
            for i in name.contents[3].contents[1].contents:
                if i != ' ' and i != '\n':
                    code2 = i.contents[1].contents[0].contents[0]
                    attributes = i.contents[3].find_all('span')
                    max_size = attributes[0].text.strip()
                    is_mandatory = "Mandatory" in attributes[1].text.strip()
                    innerClassName = i["class"]
                    if innerClassName == ['aggr', 'seg', 'edi']:
                        if i != '\n' and i != ' ':
                            group_loop(i, spaceCount + 1)#return group_loop
                    else:
                        group_loop(i, spaceCount + 1)#return group_loop
                        #output += f"</Group{i.contents[1].contents[0].contents[0][3:]}_Loop>\n"
            if isGroup:
                output+= f"</Group{name.contents[1].contents[0].contents[0][3:]}_Loop>\n"
    except:
        output += "except received\n"

URL = "https://www.truugo.com/edifact/d01b/ordrsp/"
r = requests.get(URL)
soup = BeautifulSoup(r.text, 'html.parser')

# Selecting the desired section
div_tag = soup.select_one('#view-message')#to select after #view message .


for element in div_tag.contents:
    if element != '\n' and element != ' ':
        elementClassName = element["class"]
        if elementClassName == ['aggr', 'seg', 'edi']:
            attributes = element.contents[3].find_all('span')
            max_size = attributes[0].text.strip()
            is_mandatory = "Mandatory" in attributes[1].text.strip()
            output += f"<{element.contents[1].contents[0].contents[0]} end=\"$segChar\" lastEnd=\"true\" emptyEnd=\"false\""
            if is_mandatory:
                output += f" min=\"1\""
            else:
                output += f" min=\"0\""
            output += f" max=\"{max_size}\" optionChar=\"\\r\\n\" errorLevel=\"true\">\n"
            output += f"<TAG end=\"$dataChar\" key=\"true\" min=\"1\">{element.contents[1].contents[0].contents[0]}</TAG>\n"

            for innerElement in element.contents[3].contents[1]:
                if innerElement != '\n' and innerElement != ' ':
                    class_name(innerElement)#return main function
            output +=f"</{element.contents[1].contents[0].contents[0]}>\n"
        else:
            attributes = element.contents[3].find_all('span')
            max_size = attributes[0].text.strip()
            is_mandatory = "Mandatory" in attributes[1].text.strip()
            if is_mandatory:
                min_value=1
            else:
                min_value=0
            if (element.contents[1].contents[0].contents[0][:3] == "GRP"):
                output += f"<Group{element.contents[1].contents[0].contents[0][3:]}_Loop min=\"{min_value}\""
                output +=f" max=\"{max_size}\" format=\"none\">\n"
            for innerElement in element.contents[3].contents[1]:
                if innerElement != '\n' and innerElement != ' ':
                    group_loop(innerElement, 1)#return group_loop
            output+=f"</Group{element.contents[1].contents[0].contents[0][3:]}_Loop>\n"
end_time = time.time()
elapsed_time = end_time - start_time
print(f"runtime: {elapsed_time*1000} ms")
output+='''
<UNZ end="$segChar" lastEnd="true" emptyEnd="false" min="1" optionChar="\\r\\n" errorLevel="true">
		<TAG end="$dataChar" key="true" min="1">UNZ</TAG>
		<D0036 end="$dataChar" min="1" maxSize="6" numeric="true"/>
		<D0020 end="$dataChar" min="1" maxSize="14"/>
	</UNZ>
</iXDOC>
'''
#print(output)
f = open("output.xml", "a")
f.write(output)
