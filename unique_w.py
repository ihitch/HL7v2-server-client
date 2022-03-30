# skript určený pro vypsání všech proprietálních názvů
def uniqueWords(file):
	my_File = open('/Users/jaroslav/Desktop/E-health/messages_final/'+str(file)+'.txt','r')
	read_File = my_File.read()
	words = read_File.split('|')
	unique_words = set(words)
	path3 = 'Loinc/unique_words.txt'
	soubor = open(path3,"a+")
	for word in unique_words:
		if len(word) > 4 and word[0] == '0':
			soubor.write(word+"|\n")

if __name__ == '__main__':
    uniqueWords('2011021')
    uniqueWords('2011022')
    uniqueWords('2011022B')
    uniqueWords('2011024')
    uniqueWords('2011024B')
    uniqueWords('2011032')
    uniqueWords('2011033')
    uniqueWords('2011034')
    uniqueWords('2011035')
    uniqueWords('12062011')
    my_File = open('/Users/jaroslav/Desktop/E-health/Loinc/unique_words.txt','r')
    read_File = my_File.read()
    words = read_File.split('\n')
    unique_words = set(words)
    path3 = 'Loinc/unique_words.txt'
    soubor = open(path3,"w+")
    for word in unique_words:
    	if len(word) > 4 and word[0] == '0':
    		soubor.write(word+"\n")
