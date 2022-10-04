import re
import LexicalAnalysis as LA

class SIC_CrossAssembler:

    def __init__(self, tableDict):
        self.tokenGroups = []       # 每個陣列存放一個dict{'symbol': ,'instruction': ,'operand': }
        self.tableDict = tableDict
        self.symbolTab = {}
        self.literalTab = {}
        self.opcodeTab = {}
        self.locTab = []
        self.start = ''
        self.nowloc = ''
        self.nextloc = ''
        self.instruction = {'add':[3,'18'], 'addf':[3,'58'], 'addr':[2,'90'], 'and':[3,'40'], 'clear':[2,'B4'],
                            'comp':[3,'28'], 'compf':[3,'88'], 'compr':[2,'A0'], 'div':[3,'24'], 'divf':[3,'64'], 
                            'divr':[2,'9C'], 'fix':[1,'C4'], 'float':[1,'C0'], 'hio':[1,'F4'], 'j':[3,'3C'],
                            'jeq':[3,'30'], 'jgt':[3,'34'], 'jlt':[3,'38'], 'jsub':[3,'48'], 'lda':[3,'00'],
                            'ldb':[3,'68'], 'ldch':[3,'50'], 'ldf':[3,'70'], 'ldl':[3,'08'], 'lds':[3,'6C'],
                            'ldt':[3,'74'], 'ldx':[3,'04'], 'lps':[3,'D0'], 'mul':[3,'20'], 'mulf':[3,'60'],
                            'mulr':[2,'98'], 'norm':[1,'C8'], 'or':[3,'44'], 'rd':[3,'D8'], 'rmo':[2,'AC'],
                            'rsub':[3,'4C'], 'shiftl':[2,'A4'], 'shiftr':[2,'A8'], 'sio':[1,'F0'], 'ssk':[3,'EC'],
                            'sta':[3,'0C'], 'stb':[3,'78'], 'stch':[3,'54'], 'stf':[3,'80'], 'sti':[3,'D4'],
                            'stl':[3,'14'], 'sts':[3,'7C'], 'stsw':[3,'E8'], 'stt':[3,'84'], 'stx':[3,'10'],
                            'sub':[3,'1C'], 'subf':[3,'5C'], 'subr':[2,'94'], 'svc':[2,'B0'], 'td':[3,'E0'],
                            'tio':[1,'F8'], 'tix':[3,'2C'], 'tixr':[2,'B8'], 'wd':[3,'DC']}

    def checkinstruction(self, i, locations, tempLine):
        tempDict = {}
        if locations[i][0] == '1':
            if len(locations) > 1 and locations[i+1][0] == '5':      # instruction
                if len(locations) > 3:
                    if locations[i+2][0] == '4' and locations[i+3][0] == '3': # 後面加,X的情況
                        tempDict['instruction'] = tempLine[i]
                        tempDict['operand'] = tempLine[i+1]+tempLine[i+2]+tempLine[i+3]
                        return True,1,tempDict
                    else:
                        return False
                else:
                    tempDict['instruction'] = tempLine[i]
                    tempDict['operand'] = tempLine[i+1]
                    return True,1,tempDict
            elif len(locations) > 1 and locations[i+1][0] == '4':     # 立即or間接定址法
                if tempLine[i+1] == '#' or tempLine[i+1] == '@':
                    tempDict['instruction'] = tempLine[i]
                    tempDict['operand'] = tempLine[i+1]+tempLine[i+2]
                else:
                    return False,0
            else:
                tempDict['instruction'] = tempLine[i]
                return True,1,tempDict
        elif locations[i][0] == '2':                            # pseudo
            if tempLine[i].upper() == 'START':            # 指定程式名稱和起始位置(16進位)
                if len(locations) == i+2 and locations[i+1][0] == '6':
                    tempDict['instruction'] = tempLine[i]
                    tempDict['operand'] = tempLine[i+1]
                    return True,2,tempDict
                else:
                    return False,0
            elif tempLine[i].upper() == 'END':
                if len(locations) > i+1:
                    if locations[i+1][0] == '5':
                        tempDict['instruction'] = tempLine[i]
                        tempDict['operand'] = tempLine[i+1]
                        return True,2,tempDict
                    else:
                        return False,0
                else:
                    tempDict['instruction'] = tempLine[i]
                    return True,2,tempDict
            elif tempLine[i].upper() == 'BYTE':
                try:
                    if locations[i+1][0] == '4' and (locations[i+2][0] == '6' or locations[i+2][0] == '7') and locations[i+3][0] == '4':
                        tempDict['instruction'] = tempLine[i]
                        tempDict['operand'] = tempLine[i+2]
                        return True,2,tempDict
                    return False,0
                except: 
                    return False,0
            elif tempLine[i].upper() == 'WORD':
                try:
                    if len(locations) > 0 and locations[i+1][0] == '6':
                        tempDict['instruction'] = tempLine[i]
                        tempDict['operand'] = tempLine[i+1]
                        return True,2,tempDict
                    return False,0
                except: 
                    return False,0
            elif tempLine[i].upper() == 'RESW' or tempLine[i].upper() == 'RESB':
                try:
                    if len(locations) > 0 and locations[i+1][0] == '6':
                        tempDict['instruction'] = tempLine[i]
                        tempDict['operand'] = tempLine[i+1]
                        return True,2,tempDict
                    else:
                        return False,0
                except: 
                    return False,0

    def checkSyntax(self, tempLine, line):
        source = line.split('(')    # 把Locationline切開
        del source[0]
        syntaxOK = False
        state = 0
        tempDict = {}
        if len(tempLine) > 0 and tempLine[0] == '':
            del tempLine[0]
        if len(tempLine) > 0:
            if source[0][0] == '5':     # Symbol
                syntaxOK, state, tempDict = self.checkinstruction(1, source, tempLine)
                tempDict['symbol'] = tempLine[0]
            elif tempLine[0] == '.':
                syntaxOK = True
                state = 0
            else:
                syntaxOK, state, tempDict = self.checkinstruction(0, source, tempLine)
        self.tokenGroups.append(tempDict)
        return syntaxOK, state
                
    def nextLocation(self, loc, wordNum):
        nextLoc = hex(int(loc, 16) + int(str(wordNum), 16))
        return nextLoc[2:]

    def sic_pass1(self, sourceLine, tokenLine, syntaxOK, linenum, state):
        opcode = ''
        needRelocation = False
        if len(self.tokenGroups[linenum-1]) != 0:
            if syntaxOK:
                self.nowloc = self.nextloc
                if 'START' in sourceLine:
                    self.start = tokenLine[tokenLine.index('START')+1].zfill(4)
                    self.nowloc = self.start
                    self.nextloc = self.start
                elif state == 1:        # instruction
                    if (self.tokenGroups[linenum-1]['instruction']).lower() in self.instruction.keys(): # 找instruction
                        opcode = self.instruction[self.tokenGroups[linenum-1]['instruction'].lower()][1]

                        if self.tokenGroups[linenum-1].__contains__('operand'):               # pass1看有沒有前面定義過的symbol
                            if self.tokenGroups[linenum-1]['operand'] in self.symbolTab:
                                opcode = opcode + self.symbolTab[self.tokenGroups[linenum-1]['operand']]
                            elif ',X' in self.tokenGroups[linenum-1]['operand']:              # 處理indexed
                                tempOpr = self.tokenGroups[linenum-1]['operand'].split(',')
                                if tempOpr[0] in self.symbolTab:
                                    opcode = opcode + self.nextLocation(self.symbolTab[tempOpr[0]], 8000)
                            else:
                                needRelocation = True
                        elif self.tokenGroups[linenum-1]['instruction'].lower() == 'rsub':
                            opcode = opcode + '0000'
                    
                    self.nextloc = self.nextLocation(self.nowloc, 3)
                
                elif state == 2:        # pseudo
                    if 'BYTE' in sourceLine:
                        if 'C\'' in sourceLine:
                            i = 0
                            while i < len(self.tokenGroups[linenum-1]['operand']):
                                opcode = opcode + str(hex(ord(self.tokenGroups[linenum-1]['operand'][i])))[2:].upper()
                                i += 1
                            self.nextloc = self.nextLocation(self.nowloc, i)
                        elif 'X\'' in sourceLine:
                            opcode = opcode + self.tokenGroups[linenum-1]['operand'].upper()
                            self.nextloc = self.nextLocation(self.nowloc, 1)
                    elif 'WORD' in sourceLine:
                        if int(self.tokenGroups[linenum-1]['operand']) >= 0:
                            opcode = opcode + hex(int(self.tokenGroups[linenum-1]['operand']))[2:].zfill(6).upper()
                        else:
                            opcode = opcode + hex(0xFFFFFF + int(self.tokenGroups[linenum-1]['operand']) + 1).upper()
                            
                        self.nextloc = self.nextLocation(self.nowloc, 3)
                    elif 'RESB' in sourceLine:
                        self.nextloc = self.nextLocation(self.nowloc, int(hex(int(self.tokenGroups[linenum-1]['operand']))[2:]))
                    elif 'RESW' in sourceLine:
                        self.nextloc = self.nextLocation(self.nowloc, int(self.tokenGroups[linenum-1]['operand'],16)*3)
                    
                if state == 1 or state == 2:
                    if self.tokenGroups[linenum-1].__contains__('symbol'):                    # 存進symbol
                        if self.symbolTab.__contains__(self.tokenGroups[linenum-1]['symbol']):
                            opcode = 'symbol duplicate'
                        else:
                            self.symbolTab[self.tokenGroups[linenum-1]['symbol']] = self.nowloc.upper()

            else:
                opcode = 'syntax error'
        if state != 0:
            self.opcodeTab[self.nowloc.upper()] = [opcode, needRelocation]

    def sic_pass2(self, sourceLine, tokenLine, linenum):
        outputLine = ''
        if len(self.tokenGroups[linenum-1]) != 0:
            self.nowloc = self.nextloc
            if 'START' in sourceLine:
                self.start = tokenLine[tokenLine.index('START')+1]
                self.nowloc = self.start
                self.nextloc = self.start
                outputLine = str(linenum*5)+'\t'+str(self.nowloc).upper()+'\t'+sourceLine.strip('\n')+'\t'
            elif self.tokenGroups[linenum-1]['instruction'] == 'END':
                outputLine = str(linenum*5)+'\t\t'+sourceLine.strip('\n')+'\t'
            else:
                if self.tokenGroups[linenum-1].__contains__('operand') and self.opcodeTab[self.nowloc][1] == True:               # pass1看有沒有前面定義過的symbol
                    if self.tokenGroups[linenum-1]['operand'] in self.symbolTab:
                        self.opcodeTab[self.nowloc][0] = self.opcodeTab[self.nowloc][0] + self.symbolTab[self.tokenGroups[linenum-1]['operand']]
                    elif ',X' in self.tokenGroups[linenum-1]['operand']:              # 處理indexed
                        tempOpr = self.tokenGroups[linenum-1]['operand'].split(',')
                        if tempOpr[0] in self.symbolTab:
                            self.opcodeTab[self.nowloc][0] = self.opcodeTab[self.nowloc][0] + self.nextLocation(self.symbolTab[tempOpr[0]], 8000)
                
                try:
                    self.nextloc = self.locTab[self.locTab.index(self.nowloc) + 1]
                except:
                    self.nextloc = self.nowloc
                if len(self.tokenGroups[linenum-1]) == 1:
                    outputLine = str(linenum*5)+'\t'+str(self.nowloc).upper()+'\t'+sourceLine.strip('\n')+'\t\t\t'+self.opcodeTab[self.nowloc][0][::-1]
                else:
                    outputLine = str(linenum*5)+'\t'+str(self.nowloc).upper()+'\t'+sourceLine.strip('\n')+'\t\t'+self.opcodeTab[self.nowloc][0][::-1]
        else:
            outputLine = str(linenum*5)+'\t\t'+sourceLine.strip('\n')+'\t'
        return outputLine

    def crossAssembler(self, filename, sourceList, locationList, tokens):
        i = 0
        syntaxOK = False
        state = 0       # 1:instruction, 2:pseudo, 3:symbol
        countlines = 0
        self.symbolTab = {}
        self.literalTab = {}
        self.opcodeTab = {}
        self.locTab = []
        self.tokenGroups = []
        self.start = ''
        self.nowloc = ''
        self.nextloc = ''
        fout = open('output_'+filename, 'w')
        while i < len(locationList):        # pass1
            if len(locationList) > 0 :
                if len(tokens[i]) != 0:
                    countlines+=1
                    syntaxOK, state = self.checkSyntax(tokens[i], locationList[i])
                    self.sic_pass1(sourceList[i], tokens[i], syntaxOK, countlines, state)
            i+=1
        
        fout.write('Line\tLoc\tSource statement\tObject code\n')
        i = 0
        countlines = 0
        outputLine = ''
        self.locTab = list(self.opcodeTab.keys())
        while i < len(locationList):        # pass2
            if len(locationList) > 0 :
                if len(tokens[i]) == 0:
                    fout.write('\n')
                else:
                    countlines+=1
                    outputLine = self.sic_pass2(sourceList[i], tokens[i], countlines)
                    fout.write(outputLine+'\n')
            i+=1
        fout.close()

class SICXE_CrossAssembler:

    def __init__(self, tableDict):
        self.tokenGroups = []       # 每個陣列存放一個dict{'symbol': ,'instruction': ,'operand': }
        self.tableDict = tableDict
        self.symbolTab = {}
        self.literalTab = []
        self.opcodeTab = {}
        self.locTab = []
        self.start = ''
        self.nowloc = ''
        self.nextloc = ''
        self.instruction = {'add':[3,'18'], 'addf':[3,'58'], 'addr':[2,'90'], 'and':[3,'40'], 'clear':[2,'B4'],
                            'comp':[3,'28'], 'compf':[3,'88'], 'compr':[2,'A0'], 'div':[3,'24'], 'divf':[3,'64'], 
                            'divr':[2,'9C'], 'fix':[1,'C4'], 'float':[1,'C0'], 'hio':[1,'F4'], 'j':[3,'3C'],
                            'jeq':[3,'30'], 'jgt':[3,'34'], 'jlt':[3,'38'], 'jsub':[3,'48'], 'lda':[3,'00'],
                            'ldb':[3,'68'], 'ldch':[3,'50'], 'ldf':[3,'70'], 'ldl':[3,'08'], 'lds':[3,'6C'],
                            'ldt':[3,'74'], 'ldx':[3,'04'], 'lps':[3,'D0'], 'mul':[3,'20'], 'mulf':[3,'60'],
                            'mulr':[2,'98'], 'norm':[1,'C8'], 'or':[3,'44'], 'rd':[3,'D8'], 'rmo':[2,'AC'],
                            'rsub':[3,'4C'], 'shiftl':[2,'A4'], 'shiftr':[2,'A8'], 'sio':[1,'F0'], 'ssk':[3,'EC'],
                            'sta':[3,'0C'], 'stb':[3,'78'], 'stch':[3,'54'], 'stf':[3,'80'], 'sti':[3,'D4'],
                            'stl':[3,'14'], 'sts':[3,'7C'], 'stsw':[3,'E8'], 'stt':[3,'84'], 'stx':[3,'10'],
                            'sub':[3,'1C'], 'subf':[3,'5C'], 'subr':[2,'94'], 'svc':[2,'B0'], 'td':[3,'E0'],
                            'tio':[1,'F8'], 'tix':[3,'2C'], 'tixr':[2,'B8'], 'wd':[3,'DC']}
        self.register = {'A':'0', 'X':'1', 'L':'2', 'B':'3', 'S':'4', 'T':'5', 'F':'6', 'PC':'7', 'SW':'8'}

    def checkinstruction(self, i, locations, tempLine):
        tempDict = {}
        format = 0
        if locations[i][0] == '1' or (locations[i][0] == '4' and locations[i+1][0] == '1'):
            if locations[i][0] == '4':
                i+=1
                format = 4
            else:
                format = 3
            if len(locations) > i+1 and locations[i+1][0] == '5':      # instruction
                if len(locations) > 3 and ',' in tempLine:
                    if locations[i+2][0] == '4' and locations[i+3][0] == '3': # 後面加,X的情況
                        tempDict['instruction'] = tempLine[i]
                        tempDict['operand'] = tempLine[i+1]+tempLine[i+2]+tempLine[i+3]
                        return True,1,tempDict,format
                    else:
                        return False,0,{},0
                else:
                    tempDict['instruction'] = tempLine[i]
                    tempDict['operand'] = tempLine[i+1]
                    return True,1,tempDict,format
            elif len(locations) > i+1 and (tempLine[i+1] == '#' or tempLine[i+1] == '@'):     # 立即or間接定址法
                    tempDict['instruction'] = tempLine[i]
                    tempDict['operand'] = tempLine[i+1]+tempLine[i+2]
                    return True,1,tempDict,format
            elif len(locations) > i+1 and locations[i+1][0] == '3':     # operand為register或reg,reg
                if len(locations) > 3:
                    if locations[i+2][0] == '4' and locations[i+3][0] == '3': # 後面加,X的情況
                        tempDict['instruction'] = tempLine[i]
                        tempDict['operand'] = tempLine[i+1]+tempLine[i+2]+tempLine[i+3]
                        return True,1,tempDict,format
                    else:
                        return False,0,{},0
                else:
                    tempDict['instruction'] = tempLine[i]
                    tempDict['operand'] = tempLine[i+1]
                    return True,1,tempDict,format
            elif len(locations) > i+1 and (locations[i+1][0] == '6' or tempLine[i+1] == '='):  # Literal
                if len(tempLine) > i+3 :
                    tempDict['instruction'] = tempLine[i]
                    tempDict['operand'] = tempLine[i+3]
                else:
                    tempDict['instruction'] = tempLine[i]
                    tempDict['operand'] = tempLine[i+1]
                if '=' in tempLine[i+1]:
                    self.literalTab.append(tempLine[i+2])
                else:
                    self.literalTab.append(tempLine[i+1])
                return True,1,tempDict,format
            else:
                tempDict['instruction'] = tempLine[i]
                return True,1,tempDict,format
        elif locations[i][0] == '2':                            # pseudo
            if tempLine[i].upper() == 'START':            # 指定程式名稱和起始位置(16進位)
                if len(locations) == i+2 and locations[i+1][0] == '6':
                    tempDict['instruction'] = tempLine[i]
                    tempDict['operand'] = tempLine[i+1]
                    return True,2,tempDict,0
                else:
                    return False,0,{},0
            elif tempLine[i].upper() == 'END':
                if len(locations) > i+1:
                    if locations[i+1][0] == '5':
                        tempDict['instruction'] = tempLine[i]
                        tempDict['operand'] = tempLine[i+1]
                        return True,2,tempDict,0
                    else:
                        return False,0,{},0
                else:
                    tempDict['instruction'] = tempLine[i]
                    return True,2,tempDict,0
            elif tempLine[i].upper() == 'BYTE':
                try:
                    if locations[i+1][0] == '4' and (locations[i+2][0] == '6' or locations[i+2][0] == '7') and locations[i+3][0] == '4':
                        tempDict['instruction'] = tempLine[i]
                        tempDict['operand'] = tempLine[i+2]
                        return True,2,tempDict,0
                    return False,0,{},0
                except: 
                    return False,0,{},0
            elif tempLine[i].upper() == 'WORD':
                try:
                    if len(locations) > 0 and locations[i+1][0] == '6':
                        tempDict['instruction'] = tempLine[i]
                        tempDict['operand'] = tempLine[i+1]
                        return True,2,tempDict,0
                    return False,0,{},0
                except: 
                    return False,0,{},0
            elif tempLine[i].upper() == 'RESW' or tempLine[i].upper() == 'RESB':
                try:
                    if len(locations) > 0 and locations[i+1][0] == '6':
                        tempDict['instruction'] = tempLine[i]
                        tempDict['operand'] = tempLine[i+1]
                        return True,2,tempDict,0
                    else:
                        return False,0,{},0
                except: 
                    return False,0,{},0
            elif tempLine[i].upper() == 'EQU':
                try:
                    if locations[i+1][0] == '5' or locations[i+1][0] == '6':
                        if len(tempLine) > i+2:
                            if locations[i+2][0] == '4' and (locations[i+3][0] == '5' or locations[i+3][0] == '6'):
                                tempDict['instruction'] = tempLine[i]
                                tempDict['operand'] = tempLine[i+1]+tempLine[i+2]+tempLine[i+3]
                                return True,2,tempDict,0
                        else:
                            tempDict['instruction'] = tempLine[i]
                            tempDict['operand'] = tempLine[i+1]
                            return True,2,tempDict,0
                    elif locations[i+1][0] == '4':
                        tempDict['instruction'] = tempLine[i]
                        if len(locations) > i+2:
                            tempDict['operand'] = tempLine[i+1]+tempLine[i+2]+tempLine[i+3]
                        else:
                            tempDict['operand'] = tempLine[i+1]
                        return True,2,tempDict,0
                    elif len(tempLine) > i+1:
                        if locations[i+2][0] == '4' and (locations[i+3][0] == '5' or locations[i+3][0] == '6'):
                            tempDict['instruction'] = tempLine[i]
                            tempDict['operand'] = tempLine[i+1]+tempLine[i+2]+tempLine[i+3]
                            return True,2,tempDict,0
                except:
                    return False,0,{},0
            else:
                return False,0,{},0

    def checkSyntax(self, tempLine, line):
        source = line.split('(')    # 把Locationline切開
        del source[0]
        syntaxOK = False
        state = 0
        format = 0
        tempDict = {}
        if len(tempLine) > 0 and tempLine[0] == '':
            del tempLine[0]
        if len(tempLine) > 0:
            if source[0][0] == '5':     # Symbol
                syntaxOK, state, tempDict, format = self.checkinstruction(1, source, tempLine)
                tempDict['symbol'] = tempLine[0]
            elif tempLine[0] == '*':    # 當Symbol
                try:
                    syntaxOK, state, tempDict, format = self.checkinstruction(1, source, tempLine)
                except:
                    syntaxOK = False
                tempDict['symbol'] = tempLine[0]
            elif tempLine[0] == '.':
                syntaxOK = True
                state = 0
            else:
                syntaxOK, state, tempDict, format= self.checkinstruction(0, source, tempLine)
        self.tokenGroups.append(tempDict)
        return syntaxOK, state, format

    def nextLocation(self, loc, wordNum):
        nextLoc = hex(int(loc, 16) + int(str(wordNum), 16))
        return nextLoc[2:]

    def opcodeFormat(self, format, linenum, opcode):
        if format == 1:
            opcode = opcode.upper()
            self.nextloc = self.nextLocation(self.nowloc, 1)
        elif format == 2:
            if ',' in self.tokenGroups[linenum-1]['operand']:
                operand12 = self.tokenGroups[linenum-1]['operand'].split(',')
                opcode = opcode + self.register[operand12[0].upper()] + self.register[operand12[1].upper()]
            else:
                if self.tokenGroups[linenum-1]['operand'].isdigit():
                    opcode = opcode + self.tokenGroups[linenum-1]['operand'] + '0'
                else:
                    opcode = opcode + self.register[self.tokenGroups[linenum-1]['operand'].upper()] + '0'
            self.nextloc = self.nextLocation(self.nowloc, 2)
        elif format == 3:
            if '#' in self.tokenGroups[linenum-1]['operand']:       # 立即定址n=0 i=1
                if self.tokenGroups[linenum-1]['operand'].replace('#','').isdigit():
                    opcode = hex(int(opcode,16)+1)[2:].upper().zfill(2) + '2' + hex(int(self.tokenGroups[linenum-1]['operand'].replace('#',''),16))[2:].zfill(3).upper()
                else:
                    opcode = hex(int(opcode,16)+1)[2:].upper().zfill(2) + '2' + hex(int(self.symbolTab[self.tokenGroups[linenum-1]['operand'].replace('#','')],16))[2:].zfill(3).upper()
            elif '@' in self.tokenGroups[linenum-1]['operand']:
                opcode = hex(int(opcode,16)+2)[2:].upper().zfill(2) + '2' + hex(int(self.symbolTab[self.tokenGroups[linenum-1]['operand'].replace('@','')],16)-(int(self.nowloc,16)+2))[2:].zfill(3)[-3:].upper()
            elif self.tokenGroups[linenum-1]['operand'] in self.literalTab:
                opcode = hex(int(opcode,16)+3)[2:].upper().zfill(2) + '0000'
            else:
                if int(self.symbolTab[self.tokenGroups[linenum-1]['operand']],16)-(int(self.nowloc,16)+2) >= 0:
                    opcode = hex(int(opcode,16)+3)[2:].upper().zfill(2) + '2' + hex(int(self.symbolTab[self.tokenGroups[linenum-1]['operand']],16)-(int(self.nowloc,16)+2))[2:].zfill(3)[-3:].upper()
                else:
                    opcode = hex(int(opcode,16)+3)[2:].upper().zfill(2) + '2' + hex(int('0xFFF',16)+(int(self.symbolTab[self.tokenGroups[linenum-1]['operand']],16)-(int(self.nowloc,16)+2)))[2:].upper()
            self.nextloc = self.nextLocation(self.nowloc, 3)
        elif format == 4:
            if '#' in self.tokenGroups[linenum-1]['operand']:       # 立即定址n=0 i=1
                if self.tokenGroups[linenum-1]['operand'].replace('#','').isdigit():
                    opcode = hex(int(opcode,16)+1)[2:].upper().zfill(2) + '1' + hex(int(self.tokenGroups[linenum-1]['operand'].replace('#',''),16))[2:].zfill(5).upper()
                else:
                    opcode = hex(int(opcode,16)+1)[2:].upper().zfill(2) + '1' + hex(int(self.symbolTab[self.tokenGroups[linenum-1]['operand'].replace('#','')],16))[2:].zfill(5).upper()
            elif '@' in self.tokenGroups[linenum-1]['operand']:
                opcode = hex(int(opcode,16)+3)[2:].upper().zfill(2) + '1' + hex(int(self.symbolTab[self.tokenGroups[linenum-1]['operand'].replace('@','')],16))[2:].zfill(5).upper()
            elif self.tokenGroups[linenum-1]['operand'].isdigit():
                opcode = hex(int(opcode,16)+3)[2:].upper().zfill(2) + '1' + hex(int(self.tokenGroups[linenum-1]['operand'],16))[2:].zfill(5).upper()
            else:
                opcode = hex(int(opcode,16)+3)[2:].upper().zfill(2) + '1' + hex(int(self.symbolTab[self.tokenGroups[linenum-1]['operand']],16))[2:].zfill(5).upper()
            self.nextloc = self.nextLocation(self.nowloc, 4)
        return opcode

    def sicxe_pass1(self, sourceLine, tokenLine, syntaxOK, linenum, state, format):
        opcode = ''
        instrFormat = 0
        needRelocation = False
        if len(self.tokenGroups[linenum-1]) != 0:
            if syntaxOK:
                self.nowloc = self.nextloc
                if 'START' in sourceLine:
                    self.start = tokenLine[tokenLine.index('START')+1]
                    self.nowloc = self.start
                    self.nextloc = self.start
                elif state == 1:        # instruction
                    if (self.tokenGroups[linenum-1]['instruction']).lower() in self.instruction.keys(): # 找instruction
                        instrFormat = self.instruction[self.tokenGroups[linenum-1]['instruction'].lower()][0]
                        opcode = self.instruction[self.tokenGroups[linenum-1]['instruction'].lower()][1]

                        if instrFormat == 3:        
                            instrFormat = format        # format = 3or4

                        if self.tokenGroups[linenum-1].__contains__('operand'):               # pass1看有沒有前面定義過的symbol
                            if self.tokenGroups[linenum-1]['operand'] in self.symbolTab:
                                opcode = self.opcodeFormat(instrFormat, linenum, opcode)
                            elif ',X' in self.tokenGroups[linenum-1]['operand']:              # 處理indexed
                                tempOpr = self.tokenGroups[linenum-1]['operand'].split(',')
                                if tempOpr[0] in self.symbolTab:
                                    opcode = opcode + self.nextLocation(self.symbolTab[tempOpr[0]], 8000)
                            elif self.tokenGroups[linenum-1]['operand'] in self.literalTab:
                                opcode = self.opcodeFormat(instrFormat, linenum, opcode)
                            elif instrFormat == 2:
                                opcode = self.opcodeFormat(instrFormat, linenum, opcode)
                            else:
                                needRelocation = True
                                if instrFormat == 1:
                                    self.nextloc = self.nextLocation(self.nowloc, 1)
                                elif instrFormat == 2:
                                    self.nextloc = self.nextLocation(self.nowloc, 2)
                                elif instrFormat == 3:
                                    self.nextloc = self.nextLocation(self.nowloc, 3)
                                elif instrFormat == 4:
                                    self.nextloc = self.nextLocation(self.nowloc, 4)
                        elif instrFormat == 1:
                            opcode = self.opcodeFormat(instrFormat, linenum, opcode)
                        elif self.tokenGroups[linenum-1]['instruction'].lower() == 'rsub':
                            opcode = opcode + '0000'
                    
                elif state == 2:        # pseudo
                    if 'BYTE' in sourceLine:
                        if 'C\'' in sourceLine:
                            i = 0
                            while i < len(self.tokenGroups[linenum-1]['operand']):
                                opcode = opcode + str(hex(ord(self.tokenGroups[linenum-1]['operand'][i])))[2:].upper()
                                i += 1
                            self.nextloc = self.nextLocation(self.nowloc, i)
                        elif 'X\'' in sourceLine:
                            opcode = opcode + self.tokenGroups[linenum-1]['operand'].upper()
                            self.nextloc = self.nextLocation(self.nowloc, 1)
                    elif 'WORD' in sourceLine:
                        if int(self.tokenGroups[linenum-1]['operand']) >= 0:
                            opcode = opcode + hex(int(self.tokenGroups[linenum-1]['operand']))[2:].zfill(6).upper()
                        else:
                            opcode = opcode + hex(0xFFFFFF + int(self.tokenGroups[linenum-1]['operand']) + 1).upper()
                            
                        self.nextloc = self.nextLocation(self.nowloc, 3)
                    elif 'RESB' in sourceLine:
                        self.nextloc = hex(int(self.nowloc, 16) + int(self.tokenGroups[linenum-1]['operand']))[2:]
                    elif 'RESW' in sourceLine:
                        self.nextloc = self.nextLocation(self.nowloc, int(self.tokenGroups[linenum-1]['operand'],16)*3)
                    elif 'EQU' in sourceLine:
                        if '+' not in self.tokenGroups[linenum-1]['operand'] and '-' not in self.tokenGroups[linenum-1]['operand']:
                            if self.tokenGroups[linenum-1]['operand'].isdigit():
                                self.nowloc = hex(int(self.tokenGroups[linenum-1]['operand']))[2:]
                            elif self.tokenGroups[linenum-1]['operand'].isalnum():
                                if self.tokenGroups[linenum-1]['operand']:
                                    self.nowloc = hex(int(self.tokenGroups[linenum-1]['operand'],16))[2:].upper().zfill(4)
                            else:
                                self.nowloc = self.nowloc
                        elif '-' in self.tokenGroups[linenum-1]['operand']:
                            tempOpr = self.tokenGroups[linenum-1]['operand'].split('-')
                            if tempOpr[0] in self.symbolTab and tempOpr[1] in self.symbolTab:
                                self.nowloc = hex(int(self.symbolTab[tempOpr[0]],16)-int(self.symbolTab[tempOpr[1]],16))[2:].upper().zfill(4)
                        else:
                            self.nowloc = self.nowloc
                
                if state == 1 or state == 2:
                    if self.tokenGroups[linenum-1].__contains__('symbol'):                    # 存進symbol
                        if self.symbolTab.__contains__(self.tokenGroups[linenum-1]['symbol']):
                            opcode = 'symbol duplicate'
                        else:
                            self.symbolTab[self.tokenGroups[linenum-1]['symbol']] = self.nowloc.upper()

            else:
                opcode = 'syntax error'
        #else:
            #print(str(linenum*5)+'\t'+str(self.nowloc).zfill(4).upper()+'\t'+sourceLine.strip('\n')+'\t\t\t'+opcode)
            
        if state != 0:
            self.opcodeTab[self.nowloc.upper()] = [opcode, needRelocation, instrFormat]
            #print(str(linenum*5)+'\t'+str(self.nowloc).zfill(4).upper()+'\t'+sourceLine.strip('\n')+'\t\t\t'+opcode)
        
    def sicxe_pass2(self, sourceLine, tokenLine, linenum):
        outputLine = ''
        if len(self.tokenGroups[linenum-1]) != 0:
            self.nowloc = self.nextloc
            if 'START' in sourceLine:
                self.start = tokenLine[tokenLine.index('START')+1]
                self.nowloc = self.start
                self.nextloc = self.start
                outputLine = str(linenum*5)+'\t'+str(self.nowloc).zfill(4).upper()+'\t'+sourceLine.strip('\n')+'\t'
            elif self.tokenGroups[linenum-1].__contains__('instruction') and self.tokenGroups[linenum-1]['instruction'] == 'END':
                outputLine = str(linenum*5)+'\t\t'+sourceLine.strip('\n')+'\t'
            else:
                if self.tokenGroups[linenum-1].__contains__('operand') and self.opcodeTab[self.nowloc.upper()][1] == True:       
                    if self.tokenGroups[linenum-1]['operand'] in self.symbolTab:
                        self.opcodeTab[self.nowloc.upper()][0] = self.opcodeFormat(self.opcodeTab[self.nowloc.upper()][2], linenum, self.opcodeTab[self.nowloc.upper()][0])
                    elif ',X' in self.tokenGroups[linenum-1]['operand']:              # 處理indexed
                        tempOpr = self.tokenGroups[linenum-1]['operand'].split(',')
                        if tempOpr[0] in self.symbolTab:
                            self.opcodeTab[self.nowloc.upper()][0] = self.opcodeTab[self.nowloc.upper()][0] + self.nextLocation(self.symbolTab[tempOpr[0]], 8000)
                    elif self.tokenGroups[linenum-1]['operand'] in self.literalTab:
                        self.opcodeTab[self.nowloc.upper()][0] = self.opcodeFormat(self.opcodeTab[self.nowloc.upper()][2], linenum, self.opcodeTab[self.nowloc.upper()][0])
                    elif '#' in self.tokenGroups[linenum-1]['operand'] or '@' in self.tokenGroups[linenum-1]['operand']:
                        self.opcodeTab[self.nowloc.upper()][0] = self.opcodeFormat(self.opcodeTab[self.nowloc.upper()][2], linenum, self.opcodeTab[self.nowloc.upper()][0])
                    elif self.opcodeTab[self.nowloc.upper()][2] == 2:
                        self.opcodeTab[self.nowloc.upper()][0] = self.opcodeFormat(self.opcodeTab[self.nowloc.upper()][2], linenum, self.opcodeTab[self.nowloc.upper()][0])
                    else:
                        try:
                            self.nextloc = self.locTab[self.locTab.index(self.nowloc.upper()) + 1]
                        except:
                            self.nextloc = self.nowloc                
                else:
                    try:
                        if len(self.tokenGroups) != 0:
                            self.nextloc = self.locTab[self.locTab.index(self.nowloc.upper()) + 1]
                    except:
                        self.nextloc = self.nowloc

                if len(self.tokenGroups[linenum-1]) == 1:
                    #print(str(linenum*5))
                    outputLine = str(linenum*5)+'\t'+str(self.nowloc).zfill(4).upper()+'\t'+sourceLine.strip('\n')+'\t\t\t'+self.opcodeTab[self.nowloc.upper()][0][::-1]
                else:
                    outputLine = str(linenum*5)+'\t'+str(self.nowloc).zfill(4).upper()+'\t'+sourceLine.strip('\n')+'\t\t'+self.opcodeTab[self.nowloc.upper()][0][::-1]
        else:
            outputLine = str(linenum*5)+'\t\t'+sourceLine.strip('\n')+'\t'
        return outputLine

    def crossAssembler(self, filename, sourceList, locationList, tokens):
        i = 0
        syntaxOK = False
        state = 0       # 1:instruction, 2:pseudo, 3:symbol
        format = 0
        countlines = 0
        self.symbolTab.clear()
        self.literalTab.clear()
        self.opcodeTab.clear()
        self.locTab.clear()
        self.tokenGroups.clear()
        self.start = ''
        self.nowloc = ''
        self.nextloc = ''
        fout = open('output_'+filename, 'w')
        while i < len(locationList):        # pass1
            if len(locationList) > 0 :
                if len(tokens[i]) != 0:
                    countlines+=1
                    syntaxOK, state, format = self.checkSyntax(tokens[i], locationList[i])
                    self.sicxe_pass1(sourceList[i], tokens[i], syntaxOK, countlines, state, format)
            i+=1
            
        fout.write('Line\tLoc\tSource statement\tObject code\n\n')
        i = 0
        countlines = 0
        outputLine = ''
        self.locTab = list(self.opcodeTab.keys())
        while i < len(locationList):        # pass2
            if len(locationList) > 0 :
                if len(tokens[i]) == 0:
                    fout.write('\n')
                else:
                    countlines+=1
                    outputLine = self.sicxe_pass2(sourceList[i], tokens[i], countlines)
                    fout.write(outputLine+'\n')
            i+=1
        fout.close()
        

if __name__ == "__main__":
    
    isfilefound = False
    sic_la = LA.SIC_LexicalAnalysis()
    sic_la.getTableDict(sic_la.mode, sic_la.tableDict)       # 讀入SIC table1~4
    sic_ca = SIC_CrossAssembler(sic_la.tableDict)
    sicxe_ca = SICXE_CrossAssembler(sic_la.tableDict)
    
    mode = input("\nChoose 【1:SIC, 2:SICXE, 0:exit】: " )
    while mode != "0":
        if mode == "1" or mode == "2":
            filename = input("\nPlease input a file name【0:exit】: ")
            while filename != "0":
                isFileFound = sic_la.getToken(filename)
                if isFileFound:
                    if mode == "1":
                        sic_ca.opcodeTab.clear()
                        sic_ca.crossAssembler(filename, sic_la.tempLineList, sic_la.locationLineList, sic_la.tokens)
                    elif mode == "2":
                        sicxe_ca.opcodeTab.clear()
                        sicxe_ca.crossAssembler(filename, sic_la.tempLineList, sic_la.locationLineList, sic_la.tokens)
                isFileFound = False
                filename = input("\nPlease input a file name【0:exit】: ")
        else:
            print("\nCommand not exit!")
        
        mode = input("\nChoose 【1:SIC, 2:SICXE, 0:exit】: " )
        