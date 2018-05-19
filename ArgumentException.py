
#checa se o numero digitado eh valido
def number(val):
	for i in range(len(val)):
		if(((val[i] < '0') or (val[i] >'9')) and ((val[i] != '.') and (val[i] != ','))):
			return 0;
		if(val[i] == ','):
			val[i] = '.'
	if(len(val) == 0):
		return 0;
	return 1;

def parser(linha, flag):
	aux = 0
	user1 = ''
	user2 = ''
	val = ''
	if(flag == 1): #preciso ler dois usuarios e um numero float
		for i in range(len(linha)):
			if (linha[i] == '@'): #andei ate chegar no primeiro usuario
				while((i < len(linha)) and (linha[i] != ' ')):
					if(aux == 0):
						aux = 1
					user1 += linha[i]
					i+=1
				while((i < len(linha)) and (linha[i] != '@')): #retirando o espaco em branco e os lixos de escrita ate chegar no outro @
					i += 1

				while((i < len(linha)) and (linha[i] != ' ') ):
					if(aux == 1):
						aux = 2
					user2 += linha[i]
					i+=1
				while( (i < len(linha)) and (linha[i] == ' ')): #retirando o espaco em branco
					i += 1
				while((i < len(linha))):
					if(aux == 2):
						aux = 3
					val += linha[i]
					i+=1
				break
		if((aux == 3) and (number(val) == 1)): #esse aux checa se os 3 campos foram preenchidos de maneira correta
			return {user1,user2,val}
		else:
			return -1
	elif(flag ==2): #aqui so tenho que ler um unico usuario
		for i in range(len(linha)):
			if (linha[i] == '@'): #andei ate chegar no primeiro usuario
				while((i < len(linha)) and (linha[i] != ' ') ):
					if(aux == 0):
						aux = 1
					user1 += linha[i]
					i+=1
				break
		if(aux == 1):
			return {user1, -1, -1}
		else:
			return -1
	else:
		for i in range(len(linha)):
			if (linha[i] == '@'): #andei ate chegar no primeiro usuario
				while((i < len(linha)) and (linha[i] != ' ')):
					if(aux == 0):
						aux = 1
					user1 += linha[i]
					i+=1
				while( (i < len(linha)) and (linha[i] != '@')): #retirando o espaco em branco e os lixos de escrita ate chegar no outro @
					i += 1
				while((i < len(linha)) and (linha[i] != ' ') ):
					if(aux == 1):
						aux = 2
					user2 += linha[i]
					i+=1
				break
		if((aux == 2)): #esse aux checa se os 2 campos foram preenchidos de maneira correta
			return {user1,user2, -1}
		else:
			return -1

def checa_entrada(linha,flag):
	temp = parser(linha,flag)
	if(temp == -1):
		if(flag == 1):
			print("Entrada invalida: esperado @credor @devedor valor")
		elif(flag ==2):
			print("Entrada invalida: esperado @username")
		else:
			print("Entrada invalida: esperado @credor @devedor")
		return -1
	else:
		return temp

# def main():
# 	aux = checa_entrada("@paulo", 3)


# if __name__ == '__main__':
# 	main()
