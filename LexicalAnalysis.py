############################################ 請先放入SIC和x86的Table1~4資料夾 ############################################

class LexicalAnalysis:
    
    def __init__(self):
        self.mode = 0

    def getTableDict(self, mode, tableDict):
        str = ""
        if mode == 1:       # SIC
            str = "./SIC_table/"
        elif mode == 2:     # x86
            str = "./X86table/"

        with open(str+'Table1.table', 'r') as table1:
            tableDict['Instruction'] = table1.read().splitlines()
        with open(str+'Table2.table', 'r') as table2:
            tableDict['Pseudo'] = table2.read().splitlines()
        with open(str+'Table3.table', 'r') as table3:
            tableDict['Register'] = table3.read().splitlines()
        with open(str+'Table4.table', 'r') as table4:
            tableDict['Delimiter'] = table4.read().splitlines()
        tableDict['Symbol'] = ['']*100
        tableDict['Literal'] = ['']*100
        tableDict['String'] = ['']*100

        for i in tableDict['Instruction']:      # 判斷是否讀到空白
            if ' ' in i:
                tableDict['Instruction'][tableDict['Instruction'].index(i)] = i.strip()
        for i in tableDict['Pseudo']:
            if ' ' in i:
                tableDict['Pseudo'][tableDict['Pseudo'].index(i)] = i.strip()
        for i in tableDict['Register']:
            if ' ' in i:
                tableDict['Register'][tableDict['Register'].index(i)] = i.strip()
        for i in tableDict['Delimiter']:
            if ' ' in i:
                tableDict['Delimiter'][tableDict['Delimiter'].index(i)] = i.strip()

        return tableDict  

    def countIndex(self, tableKey, str):
        tempSum = 0
        for j in range(len(str)):
            tempSum = tempSum + ord(str[j])
        tempIndex = tempSum % 100
        while self.tableDict[tableKey][tempIndex] != '' and self.tableDict[tableKey][tempIndex] != str:
            if tempIndex == 99:
                tempIndex=0
            else:
                tempIndex+=1
        if self.tableDict[tableKey][tempIndex] != str:
            self.tableDict[tableKey][tempIndex] = str
        return tempIndex
    
    def strBufferCompare(self, mode, strBuffer, locationLine):
        if mode == 1 and strBuffer.lower() in self.tableDict['Instruction']:
            locationLine = locationLine + "(1," + str(self.tableDict['Instruction'].index(strBuffer.lower())+1) + ")"
        elif mode == 2 and strBuffer.upper() in self.tableDict['Instruction']:
            locationLine = locationLine + "(1," + str(self.tableDict['Instruction'].index(strBuffer.upper())+1) + ")"
        elif strBuffer.upper() in self.tableDict['Pseudo']:
            locationLine = locationLine + "(2," + str(self.tableDict['Pseudo'].index(strBuffer.upper())+1) + ")"
        elif strBuffer.upper() in self.tableDict['Register']:
            locationLine = locationLine + "(3," + str(self.tableDict['Register'].index(strBuffer.upper())+1) + ")"
        elif strBuffer in self.tableDict['Symbol']:
            locationLine = locationLine + "(5," + str(self.tableDict['Symbol'].index(strBuffer)) + ")"
        elif strBuffer in self.tableDict['Literal']:
            locationLine = locationLine + "(6," + str(self.tableDict['Literal'].index(strBuffer)) + ")"
        elif strBuffer in self.tableDict['String']:
            locationLine = locationLine + "(7," + str(self.tableDict['String'].index(strBuffer)) + ")"
        else:
            ishex = False
            if strBuffer[-1].upper() == 'H':
                ishex = True
                for i in range(len(strBuffer)-1):
                    if not(strBuffer[i] >= '0' and strBuffer[i] <= '9') and not(strBuffer[i] >= 'A' and strBuffer[i] <= 'F') and not(strBuffer[i] >= 'a' and strBuffer[i] <= 'f'):
                        ishex = False

            if mode == 2 and ishex == True:
                tempIndex = self.countIndex('Literal', strBuffer) #[:-2]
                locationLine = locationLine + "(6," + str(tempIndex) + ")"
            elif strBuffer.isalpha():       # 若token為字母，加入Symbol
                tempIndex = self.countIndex('Symbol', strBuffer)
                locationLine = locationLine + "(5," + str(tempIndex) + ")"
            elif strBuffer.isdigit():     # 若token為digit，加入Literal
                tempIndex = self.countIndex('Literal', strBuffer)
                locationLine = locationLine + "(6," + str(tempIndex) + ")"
            elif mode == 1 and strBuffer.isalnum():
                tempIndex = self.countIndex('Symbol', strBuffer)
                locationLine = locationLine + "(5," + str(tempIndex) + ")"
            
        return locationLine

    def printLocation(self, filename):
        fout = open('output_'+filename, 'w')
        i = 0
        while i < len(self.tempLineList):
            fout.write(self.tempLineList[i])
            fout.write(self.locationLineList[i]+"\n")
            i+=1
        fout.close()

class SIC_LexicalAnalysis(LexicalAnalysis):

    def __init__(self):
        self.mode = 1
        self.tableDict = {'Instruction':[], 'Pseudo':[], 'Register':[], 'Delimiter':[], 'Symbol':[], 'Literal':[], 'String':[]}
        self.tempLineList = []
        self.locationLineList = []
        self.tokens = []

    def getToken(self, filename):
        try:
            with open(filename,'r') as fin:
                strBuffer = ""
                locationLine = ""
                tempLine = fin.readline()
                while tempLine != '':        
                    if tempLine[-1] != '\n':
                        tempLine = tempLine + '\n'
                    i = 0
                    tempToken = []
                    while i < len(tempLine):
                        s = tempLine[i]
                        if tempLine[i] == ' ' or tempLine[i] == '\t' or tempLine[i] == '\n':    # 判斷buffer是否有token
                            if strBuffer != "":
                                locationLine = self.strBufferCompare(self.mode, strBuffer, locationLine)     # 判斷buffer是否在table或要加入table
                                tempToken.append(strBuffer)
                            strBuffer = ""
                        elif tempLine[i] in self.tableDict['Delimiter']:
                            if tempLine[i] == '\'':         # 判斷單引號
                                locationLine = locationLine + "(4," + str(self.tableDict['Delimiter'].index(tempLine[i])+1) + ")"
                                tempToken.append(tempLine[i])
                                tempStr = ""
                                i+=1
                                while i < len(tempLine) and tempLine[i] != '\'':
                                    tempStr = tempStr + tempLine[i]
                                    i+=1
                                if tempLine[i] == '\'' and (strBuffer == 'C' or strBuffer == ''):
                                    tempIndex = self.countIndex('String', tempStr)
                                    locationLine = locationLine + "(7," + str(tempIndex) + ")(4," + str(self.tableDict['Delimiter'].index(tempLine[i])+1) + ")"
                                    tempToken.append(tempStr)
                                    tempToken.append(tempLine[i])
                                elif tempLine[i] == '\'' and strBuffer == 'X':
                                    tempIndex = self.countIndex('Literal', tempStr)
                                    locationLine = locationLine + "(6," + str(tempIndex) + ")(4," + str(self.tableDict['Delimiter'].index(tempLine[i])+1) + ")"
                                    tempToken.append(tempStr)
                                    tempToken.append(tempLine[i])
                                else:
                                    print("error")
                                strBuffer = ""
                            elif tempLine[i] == '.':        # 判斷註解
                                locationLine = locationLine + "(4," + str(self.tableDict['Delimiter'].index(tempLine[i])+1) + ")"
                                tempToken.append(tempLine[i])
                                i+=1
                                while i < len(tempLine) and tempLine[i] != '\n':
                                    i+=1
                            else:                           # 判斷其他
                                if len(strBuffer) != 0:
                                    locationLine = self.strBufferCompare(self.mode, strBuffer, locationLine)
                                    tempToken.append(strBuffer)
                                locationLine = locationLine + "(4," + str(self.tableDict['Delimiter'].index(tempLine[i])+1) + ")"
                                tempToken.append(tempLine[i])
                                strBuffer = ""
                        elif tempLine[i].isalpha() or tempLine[i].isdigit():
                            strBuffer = strBuffer + tempLine[i]
                            
                        i+=1
                    
                    if len(tempToken) > 0 and tempToken[0] == 'LTORG':
                        pass
                    self.tempLineList.append(tempLine)
                    self.tokens.append(tempToken)
                    self.locationLineList.append(locationLine)
                    locationLine = ""
                    tempLine = fin.readline()
            print("\nOutput file to: output_"+filename)
            return True
        except FileNotFoundError:
            print('\n'+ filename + ' not exists!')


class X86_LexicalAnalysis(LexicalAnalysis):
    def __init__(self):
        self.mode = 2
        self.tableDict = {'Instruction':[], 'Pseudo':[], 'Register':[], 'Delimiter':[], 'Symbol':[], 'Literal':[], 'String':[]}
        self.tempLineList = []
        self.locationLineList = []

    def getToken(self, filename):
        try:
            with open(filename,'r') as fin:
                strBuffer = ""
                locationLine = ""
                tempLine = fin.readline()
                while tempLine != '':        
                    if tempLine[-1] != '\n':
                        tempLine = tempLine + '\n'
                    i = 0
                    while i < len(tempLine):
                        s = tempLine[i]
                        if tempLine[i] == ' ' or tempLine[i] == '\t' or tempLine[i] == '\n':    # 判斷buffer是否有token
                            if strBuffer != "":
                                locationLine = self.strBufferCompare(self.mode, strBuffer, locationLine)     # 判斷buffer是否在table或要加入table
                            strBuffer = ""
                        elif tempLine[i] in self.tableDict['Delimiter']:
                            if len(strBuffer) != 0:
                                    locationLine = self.strBufferCompare(self.mode, strBuffer, locationLine)
                                    strBuffer = ""

                            if tempLine[i] == '\'':         # 判斷單引號
                                locationLine = locationLine + "(4," + str(self.tableDict['Delimiter'].index(tempLine[i])+1) + ")"
                                tempStr = ""
                                i+=1
                                while i < len(tempLine) and tempLine[i] != '\'':
                                    tempStr = tempStr + tempLine[i]
                                    i+=1
                                tempIndex = self.countIndex('String', tempStr)
                                locationLine = locationLine + "(7," + str(tempIndex) + ")(4," + str(self.tableDict['Delimiter'].index(tempLine[i])+1) + ")"
                            elif tempLine[i] == ';':        # 判斷註解
                                locationLine = locationLine + "(4," + str(self.tableDict['Delimiter'].index(tempLine[i])+1) + ")"
                                i+=1
                                while i < len(tempLine) and tempLine[i] != '\n':
                                    i+=1
                            else:                           # 判斷其他
                                locationLine = locationLine + "(4," + str(self.tableDict['Delimiter'].index(tempLine[i])+1) + ")"
                        elif tempLine[i].isalpha() or tempLine[i].isdigit():
                            strBuffer = strBuffer + tempLine[i]
                            
                        i+=1

                    #fout.write(tempLine+locationLine+"\n")
                    self.tempLineList.append(tempLine)
                    self.locationLineList.append(locationLine)
                    locationLine = ""
                    tempLine = fin.readline()
            print("\nOutput file to: output_"+filename)
            #fout.close()
        except FileNotFoundError:
            print('\n'+ filename + ' not exists!')

if __name__ == "__main__":

    sic_la = SIC_LexicalAnalysis()
    sic_la.getTableDict(sic_la.mode, sic_la.tableDict)       # 讀入SIC table1~4
    x86_la = X86_LexicalAnalysis()
    x86_la.getTableDict(x86_la.mode, x86_la.tableDict)       # 讀入x86 table1~4
    mode = input("\nChoose 【1:SIC, 2:X86, 0:exit】: " )

    while mode != "0":
        if mode == "1" or mode == "2":
            filename = input("\nPlease input a file name【0:exit】: ")
            while filename != "0":
                if mode == "1":
                    sic_la.getToken(filename)
                    sic_la.printLocation(filename)
                    sic_la.tempLineList.clear()
                    sic_la.locationLineList.clear()
                elif mode == "2":
                    x86_la.getToken(filename)
                    x86_la.printLocation(filename)
                    x86_la.tempLineList.clear()
                    x86_la.locationLineList.clear()
                filename = input("\nPlease input a file name【0:exit】: ")
        else:
            print("\nCommand not exit!")
        
        mode = input("\nChoose 【1:SIC, 2:X86, 0:exit】: " )

        