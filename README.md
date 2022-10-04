# SIC-XE-Assembler
模擬翻譯 SIC 及 SIC/XE 組合語言的組譯器，在檢查語法是否有誤後，翻成 Object code，而 SIC/XE 較 SIC 需多區分 format。架構上分成pass 1、pass 2，pass 1 將指令定址後，pass 2 分析並翻成 Object code 輸出。
