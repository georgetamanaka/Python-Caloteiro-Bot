#linha = update.message.txt

#checa se o numero digitado eh valido
def number(val):
	for i in range(len(val)):
		if((val[i] < '0') or (val[i] >'9') or (val[i] != '.') or (val[i] != ',')):
			return 0;
	return 1;

def funcao(linha):
	aux
	user1 = ''
	user2 = ''
	val = ''
	for i in range(len(linha)):
		if linha[i] == '@': #andei ate chegar no primeiro usuario
			while((linha[i] != ' ') and (i < len(linha))):
				if(aux == 0):
					aux = 1
				user1 += linha[i]
				i+=1
			while((linha[i] != '@') and (i < len(linha))): #retirando o espaco em branco e os lixos de escrita ate chegar no outro @
				i += 1
			while((linha[i] != ' ') and (i < len(linha))):
				if(aux == 1):
					aux = 2
				user2 += linha[i]
				i+=1
			while((linha[i] == ' ') and (i < len(linha))): #retirando o espaco em branco
				i += 1
			while((i < len(linha))):
				if(aux == 2):
					aux = 3
				val += linha[i]
				i+=1

	if((aux == 3) and (number(val) == 1)): #esse aux checa se os 3 campos foram preenchidos de maneira correta
		print(user1)
		print(user2)
		print(val)
	else:
		print("entrada invalida")