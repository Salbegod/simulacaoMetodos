class compara:
    for i in range(1, 201):

        with open('saida.txt', 'r') as arquivo:
            linhas = arquivo.readlines()
        with open('saida2.txt', 'r') as arquivo:
            linhas2 = arquivo.readlines()
        for i in range(0, 200):
            if linhas[i] != linhas2[i]:
                with open('compara.txt', 'a') as arquivo:
                    print("{}\n1 - {}2 - {}".format(i+1, linhas[i], linhas2[i]), file=arquivo)