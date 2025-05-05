from random import shuffle, randrange
from math import ceil 
# ceil - > arredondar p cima

# TODO - Colocar tropas DONE
# TODO - ATUALIZAR O HUD DONE
# TODO - ARRUMAR O COLOCAR TROPAS DONE
# TODO - ATUALIZAR EXIBICAO DE COLOCAR TROPAS
# TODO - Atacar DONE
# TODO - transferir territorios DONE
# TODO - Trocar jogador DONE

# TODO - Transferir tropas
# TODO - bonus por continente #

# TODO - jogador nao pode atacar o proprio territorio
# TOD - mostrar territorios disponiveis para atacar

class Jogador:
    def __init__(self,nome):
        self.nome = nome
        self.territorios = []

    # organizar/ordenar as cartas
    def organizar_cartas(self):
        self.territorios.sort(key= encontrar_id)

    # posicionar as tropas nos territorios
    def colocar_tropas(self, grupos):
        tropas_disponiveis = self.calcular_tropas()
        self.colocar_tropas_bonus(grupos)
        while tropas_disponiveis > 0:
            print("\nTropas disponíveis: "+str(tropas_disponiveis))
            while True:
                print("\nEscolha um territorio para colocar tropas \n")
                escolha = int(input())
                local_posicionamento = self.encontrar_territorio(escolha)
                if local_posicionamento == False:
                    print("Escolha invalida")
                else:
                    break
        
            
            quantidade_tropas_posicionamento = int(input("\nQuantas tropas deseja colocar? (0 para cancelar)"))
            if quantidade_tropas_posicionamento > tropas_disponiveis:
                print("\nQuantidade insuficiente!")
            local_posicionamento.tropas += quantidade_tropas_posicionamento
            tropas_disponiveis -= quantidade_tropas_posicionamento
            print("\nTropas posicionadas\n")
            mostrar_territorios(self, grupos)
        print("\nTodas as tropas posicionadas\n")
        input("\nPresssione qualquer tecla")
    
    def colocar_tropas_bonus(self, grupos):
        for grupo in grupos:
            grupo.posicionamento_bonus(self.nome)

    # quantas serao colocadas
    def calcular_tropas(self):
        return ceil(len(self.territorios)/2)

    def atacar(self, jogadores, territorios, grupos):
        while True:

            while True:
                id_territorio_atacante = int(input("\nEscolha de onde vai atacar(0 cancela)"))
                if id_territorio_atacante == 0:
                    break
                territorio_atacante =  self.encontrar_territorio(id_territorio_atacante)
                if territorio_atacante == False:
                    print("\nLocal inválido")
                else:
                    break
            # CANCELAR ESCOLHA
            if id_territorio_atacante == 0:
                break

            while True:
                conexoes = territorio_atacante.exibir_conexoes_ataque(territorios, self)
                if conexoes == []:
                    print("Não existem alvos disponiveis")
                    id_alvo = 0
                    break
                id_alvo = int(input("\nEscolha um alvo(0 para cancelar)"))
                if id_alvo not in conexoes or id_alvo == territorio_atacante.id:
                    print("\nId inválido\n")
                else:
                    break
            if id_alvo == 0:
                continue # cancela, volta do inico

            jogador_defensor = encontrar_dono_territorio(id=id_alvo,jogadores=jogadores)
            if jogador_defensor.nome == self.nome:
                print("Não pode atacar a si mesmo") # autoexplicativo
                continue
            territorio_atacado = jogador_defensor.encontrar_territorio(id_alvo)
            tropas_defensoras = territorio_atacado.tropas
            if tropas_defensoras > 3:
                tropas_defensoras = 3

            while True:
                numero_dados_ataque = int(input("\nQuantas tropas usar?"))
                if numero_dados_ataque > 3 or numero_dados_ataque > territorio_atacante.tropas:
                    print("\nNumero inválido")
                else:
                    break
        
            resultado_ataque = self.rolar_dados(numero_dados_ataque)
            resultado_defesa = jogador_defensor.rolar_dados(tropas_defensoras)
            if resultado_defesa >= resultado_ataque:
                vencedor = "defesa"
            else:
                vencedor = "ataque"
                territorio_atacado.tropas -= tropas_defensoras
                print(f"\nTropas restantes {territorio_atacado.nome} = {territorio_atacado.tropas}")
            print(f"""\n\n
                atacante: {resultado_ataque}
                defensor: {resultado_defesa}
                vencedor: {vencedor}
    """)    
            if territorio_atacado.tropas == 0:
                transferir_territorio(territorio_atacado, jogador_defensor, self)
            if vencedor == "defesa":
                print("Atacante perdeu, não pode mais atacar")
                break
            else:
                mostrar_territorios(self, grupos)
        print("Encerrando ataques")


    # TODO

    def encontrar_territorio(self, id):
        if id == 0:
            return 0
        for i in self.territorios:
            if i.id == id:
                return i
        return "n/a"


    def rolar_dados(self, n_dados):
        resultado_dados = 0
        for i in range(n_dados):
            resultado_dados += randrange(1,7)
        return resultado_dados
    
    def transferir_tropas(self, grupos):
        while True:
            locais_disponiveis = []
            print("\nEscolha um local de origem das tropas para realocar (0 para cancelar)")
            local_origem = self.encontrar_territorio(int(input()))
            if local_origem == 0:
                break
            if local_origem == "n/a":
                print("Territorio invalido")
                continue
            if local_origem.tropas == 1:
                print("Tropas não disponiveis para transferencia")
                continue
            locais_disponiveis = local_origem.exibir_conexoes_transferencia(self.territorios)
            if locais_disponiveis == []:
                continue

            while True:
                destino = self.encontrar_territorio(int(input("\nEscolha um destino")))
                if destino == ("n/a"):
                    print("\nSeleção invalida")
                    continue
                else:
                    break
            if destino == 0:
                continue
            tropas_maximas = local_origem.tropas - 1
            tropas = int(input(f"Quantas troaps? (max {tropas_maximas})"))
            if tropas > tropas_maximas:
                print("Valor invalido")
                continue

            local_origem.tropas -= tropas
            destino.tropas += tropas

            mostrar_territorios(self, grupos)
        print("Fim posicionamento")
        

# facilitar a controlar os dados dos territorios
class Territorio:
    def __init__(self, nome, grupo, conexoes, id):
        self.nome = nome
        self.id = id
        self.grupo = grupo
        self.conexoes = conexoes
        self.tropas = 1
        self.dono = ""

    def exibir_conexoes_ataque(self, territorios, jogador_atacante):
        conexoes = []
        for i in territorios:
            if i.nome in self.conexoes:
                if i.dono == jogador_atacante.nome:
                    continue
                print(f"\t-> {i.id} - {i.nome} ({i.tropas} -- {i.dono})")
                conexoes.append(i.id)
        return conexoes
    
    def exibir_conexoes_transferencia(self, territorios):
        conexoes = []
        for i in territorios:
            if i.nome in self.conexoes and i.dono == self.dono:
                print(f"\t-> {i.id} - {i.nome} ({i.tropas})")
                conexoes.append(i)
        if conexoes == []:
            print("Nenhum local disponivel")
        return conexoes

    def atualizar_dono(self, jogador):
        self.dono = jogador.nome
        print(f"Jogador {jogador.nome} adiquiriu pose de {self.nome}")
    
class Grupo:
    def __init__(self, nome, bonus):
        self.nome = nome
        self.territorios = []
        self.id_territorios = []
        self.bonus = bonus
        
    def coletar_ids(self):
        for i in self.territorios:
            self.id_territorios.append(i.id)

    
    def exibir_bonus(self, nome_jogador):
        if self.validar_bonus(nome_jogador) == True:
            return f"+{self.bonus}"
        else:
            return "  "

    def validar_bonus(self, nome_jogador):
        for territorio in self.territorios:
            if nome_jogador != territorio.dono:
                return False
        return True
        
    def posicionamento_bonus(self, nome_jogador):
        escolha_posicionamento = 0
        local_posicionamento = ""
        pecas_disponiveis = self.bonus
        pecas_colocando = ""


        if self.validar_bonus(nome_jogador) != True:
            return None
        print(f"\n->Posicionamento bonus em {self.nome} -  Coloque +{self.bonus} tropas em qualquer território do grupo!")
        while pecas_disponiveis > 0:
            while True:
                escolha_posicionamento = int(input("\nEscolha um local"))
                if escolha_posicionamento not in self.id_territorios:
                    print("\n>Escolha invalida")
                else:
                    for i in self.territorios:
                        if i.id == escolha_posicionamento:
                            local_posicionamento = i
                            break
                    break
            while True:
                pecas_colocando = int(input(f"\nQuantas pecas colocar? (Restantes -> {pecas_disponiveis})"))
                if pecas_colocando > pecas_disponiveis:
                    print("\n<Numero inválido")
                else:
                    local_posicionamento.tropas += pecas_colocando
                    pecas_disponiveis -= pecas_colocando
                    break
        print("\nBonus colocado!!\n")



NUMERO_JOGADORES = 2

locais_nomes = [
    "Colditz","Frankfurt","Fulda",
    "Hedeby","Nonnebakken","Fyrkat","Trelleborg","Ilhas Farreyjar",
    "Hlioarendi","Papey","Akureyri","Borg","Reykjavik","Haukadalur",
    "Lund","Helgo","Stockholm","Sigtuna","Gamla Upsala","Valsgarde","Umea",
    "Lindisfarne","York","Leicester","Londres","Cork","Wexford","Dublin","Sligo",
    "Stavanger","Kaupang","Bergen","Oslo","Trondheim","Ornes","Trondenes"
    ]

grupos_informacoes = {
    "Alemanha" : {
        "nome" : "Alemanha",
        "Terras" : 3,
        "Bonus" : 1
    },
    "Dinamarca" : {
        "nome" : "Dinamarca",
        "Terras" : 5,
        "Bonus" : 2
    },
    "Islândia" : {
        "nome" : "Islândia",
        "Terras" : 6,
        "Bonus" : 3
    },
    "Suécia" : {
        "nome" : "Suécia",
        "Terras" : 7,
        "Bonus" : 4
    },
    "Ilhas Britânicas" : {
        "nome" : "Ilhas Britânicas",
        "Terras" : 8,
        "Bonus" : 5
    },
    "Noruega" : {
        "nome" : "Noruega",
        "Terras" : 7,
        "Bonus" : 6
    }




}
# achar o local pelo id
locais_informacoes = {
    # Alemanha
    1 : {
        "nome" : "Colditz",
        "grupo" : "Alemanha",
        "conexoes" : ["Frankfurt"]
    },
    2 : {
        "nome" : "Frankfurt",
        "grupo" : "Alemanha",
        "conexoes" : ["Colditz", "Fulda"]
    },
    3 : {
        "nome" : "Fulda",
        "grupo" : "Alemanha",
        "conexoes" : ["Frankfurt", "Hedeby", "Leicester"]
    },
    # Dinamarca
    4 : {
        "nome" : "Hedeby",
        "grupo" : "Dinamarca",
        "conexoes" : ["Fulda", "Nonnebakken"]
    },
    5 : {
        "nome" : "Nonnebakken",
        "grupo" : "Dinamarca",
        "conexoes" : ["Hedeby", "Fyrkat"]
    },
    6 : {
        "nome" : "Fyrkat",
        "grupo" : "Dinamarca",
        "conexoes" : ["Nonnebakken", "Trelleborg", "Ilhas Farreyjar", "York"]
    },
    7 : {
        "nome" : "Trelleborg",
        "grupo" : "Dinamarca",
        "conexoes" : ["Fyrkat", "Lund"]
    },
    8 : {
        "nome" : "Ilhas Farreyjar",
        "grupo" : "Dinamarca",
        "conexoes" : ["Fyrkat", "Lindisfarne", "Hlioarendi", "Papey", "Trondheim"]
    },
    # Islandia
    9 : {
        "nome" : "Hlioarendi",
        "grupo" : "Islândia",
        "conexoes" : ["Ilhas Farreyjar", "Papey", "Haukadalur", "Reykjavik"]
    },
    10 : {
        "nome" : "Papey",
        "grupo" : "Islândia",
        "conexoes" : ["Hlioarendi", "Haukadalur" ,"Akureyri", "Ilhas Farreyjar"]
    },
    11 : {
        "nome" : "Akureyri",
        "grupo" : "Islândia",
        "conexoes" : ["Borg", "Haukadalur", "Papey", "Ornes"]
    },
    12 : {
        "nome" : "Borg",
        "grupo" : "Islândia",
        "conexoes" : ["Akureyri", "Haukadalur", "Reykjavik"]
    },
    13 : {
        "nome" : "Reykjavik",
        "grupo" : "Islândia",
        "conexoes" : ["Borg", "Haukadalur", "Hlioarendi", "Lindisfarne", "Sligo"],
    },
    14 : {
        "nome" : "Haukadalur",
        "grupo" : "Islândia",
        "conexoes" : ["Borg", "Akureyri", "Papey", "Hlioarendi", "Reykjavik"]
    },
    # Suécia
    15 : {
        "nome" : "Lund",
        "grupo" : "Suécia",
        "conexoes" : ["Trelleborg", "Helgo", "Stockholm"]
    },
    16 : {
        "nome" : "Helgo",
        "grupo" : "Suécia",
        "conexoes" : ["Lund", "Stockholm", "Sigtuna", "Oslo"]
    },
    17 : {
        "nome" : "Stockholm",
        "grupo" : "Suécia",
        "conexoes" : ["Helgo", "Lund", "Sigtuna"]
    },
    18 : {
        "nome" : "Sigtuna",
        "grupo" : "Suécia",
        "conexoes" : ["Stockholm", "Helgo", "Gamla Upsala", "Oslo", "Trondheim"]
    },
    19 : {
        "nome" : "Gamla Upsala",
        "grupo" : "Suécia",
        "conexoes" : ["Sigtuna", "Valsgarde","Trondheim", "Ornes"]
    },
    20 : {
        "nome" : "Valsgarde",
        "grupo" : "Suécia",
        "conexoes" : ["Gamla Upsala", "Umea","Ornes", "Trondenes"]
    },
    21 : {
        "nome" : "Umea",
        "grupo" : "Suécia",
        "conexoes" : ["Valsgarde", "Ornes", "Trondenes"]
    },
    # Ilhas Britânicas
    22 : {
        "nome" : "Lindisfarne",
        "grupo" : "Ilhas Britânicas",
        "conexoes" : ["Ilhas Farreyjar", "Reykjavik", "Stavanger", "Sligo", "York"]
    },
    23 : {
        "nome" : "York",
        "grupo" : "Ilhas Britânicas",
        "conexoes" : ["Lindisfarne", "Leicester", "Dublin", "Fyrkat"]
    },
    24 : {
        "nome" : "Leicester",
        "grupo" : "Ilhas Britânicas",
        "conexoes" : ["York", "Londres", "Fulda"]
    },
    25 : {
        "nome" : "Londres",
        "grupo" : "Ilhas Britânicas",
        "conexoes" : ["Leicester", "Cork"]
    },
    26 : {
        "nome" : "Cork",
        "grupo" : "Ilhas Britânicas",
        "conexoes" : ["Londres", "Wexford"]
    },
    27 : {
        "nome" : "Wexford",
        "grupo" : "Ilhas Britânicas",
        "conexoes" : ["Cork", "Dublin"]
    },
    28 : {
        "nome" : "Dublin",
        "grupo" : "Ilhas Britânicas",
        "conexoes" : ["Wexford", "York", "Sligo"]
    },
    29 : {
        "nome" : "Sligo",
        "grupo" : "Ilhas Britânicas",
        "conexoes" : ["Dublin", "Lindisfarne", "Reykjavik"]
    },
    # Noruega
    30 : {
        "nome" : "Stavanger",
        "grupo" : "Noruega",
        "conexoes" : ["Lindisfarne", "Kaupang", "Bergen"]
    },
    31 : {
        "nome" : "Kaupang",
        "grupo" : "Noruega",
        "conexoes" : ["Stavanger", "Bergen", "Oslo"]
    },
    32 : {
        "nome" : "Bergen",
        "grupo" : "Noruega",
        "conexoes" : ["Kaupang", "Oslo", "Trondheim"]
    },
    33 : {
        "nome" : "Oslo",
        "grupo" : "Noruega",
        "conexoes" : ["Bergen", "Kaupang", "Trondheim", "Sigtuna", "Helgo"],
    },
    34 : {
        "nome" : "Trondheim",
        "grupo" : "Noruega",
        "conexoes" : ["Oslo", "Bergen", "Ornes", "Ilhas Farreyjar", "Sigtuna", "Gamla Upsala"]
    },
    35 : {
        "nome" : "Ornes",
        "grupo" : "Noruega",
        "conexoes" : ["Trondheim", "Trondenes", "Akureyri", "Gamla Upsala", "Valsgarde"]
    },
    36 : {
        "nome" : "Trondenes",
        "grupo" : "Noruega",
        "conexoes" : ["Ornes", "Valsgarde", "Umea"]
    }
    }

# transferir apos ataque succedido
def transferir_territorio(territorio, jogador_defensor, jogador_atacante):
    jogador_defensor.territorios.remove(territorio)
    jogador_atacante.territorios.append(territorio)
    territorio.atualizar_dono(jogador_atacante)
    input("Pressione qualquer tecla")

def andamento_partida(jogadores,territorios, grupos):
    for jogador in jogadores:
        rodada_jogador(jogador_atual=jogador, jogadores=jogadores,territorios=territorios, grupos=grupos)

def rodada_jogador(jogador_atual, jogadores, territorios, grupos):
    menu_jogador(jogador_atual, grupos=grupos)
    jogador_atual.colocar_tropas(grupos)
    jogador_atual.atacar(jogadores,territorios, grupos)
    jogador_atual.transferir_tropas(grupos)


# ajudar a organizar os territorios
def encontrar_id(objeto):
        return objeto.id 

# encontrar o territorio com base no nome dado
def encontrar_territorio(nome, territorios):
    for i in territorios:
        if i.nome == nome:
            return i

# encontrar qual jogador é o dono do territorio X
def encontrar_dono_territorio(id, jogadores):
    for jogador in jogadores:
        for territorio in jogador.territorios:
            if id == territorio.id:
                return jogador

# encontrar o grupo relativo ao nome X
def encontrar_grupo_territorios(nome_grupo, grupos):
    for i in grupos:
        if i.nome == nome_grupo:
            return i

# verificar/validar que todos os ataques sejam possiveis, evitando erros
def verificar_conexoes(lugares, nomes):
    for ataque in lugares:
        print(f"Teste: {ataque}")
        for origem in lugares[ataque]["conexoes"]:
            for destinos in nomes:
                if destinos == origem:
                    teste = True
                    break
                else:
                    teste = False
            print(f"    -> {origem}: {teste}")

# criar os objetos jogadores
def criar_jogadores(n_jogadores):
    jogadores = []
    cores_jogadores ={
        0 : "Amarelo",
        1 : "Azul",
        2 : "Preto",
        3 : "Vermelho"
    }
    
    for i in range(0, n_jogadores):
        jogadores.append(Jogador(cores_jogadores[i]))

    return(jogadores) # armazenar os jogadores que forem criados

# criar os objetos territorios
def preparar_territorios(dados_territorios):
    territorios = []
    for i in dados_territorios:
        territorio = Territorio(dados_territorios[i]["nome"],dados_territorios[i]["grupo"],dados_territorios[i]["conexoes"], i)
        territorios.append(territorio)
    return territorios

def criar_grupos_territorios(territorios, grupos_dados):
    grupos = []
    for i in grupos_dados:
        novo_grupo = Grupo(nome=grupos_dados[i]["nome"], bonus=grupos_dados[i]["Bonus"])
        for terra in territorios:
            if terra.grupo == novo_grupo.nome:
                novo_grupo.territorios.append(terra)
        novo_grupo.coletar_ids() # salvar ids dos seus territorios
        grupos.append(novo_grupo)
    return grupos

def dividir_territorios(lugares, objetos_territorios, jogadores):
    id_territorios = []
    territorios = []

    # coletar o id de cada territorio e colocar em um grupo
    for id in lugares:
        id_territorios.append(id)
    shuffle(id_territorios) # os ids das cartas
    divisao_cartas = (int(len(id_territorios)/len(jogadores)))

    for jogador in jogadores:
        for i in range(divisao_cartas):
            numero_territorio = id_territorios.pop()
            jogador.territorios.append(objetos_territorios[numero_territorio-1])


    return(territorios) # retornar monte

# criar jogadores e dividir as cartas
def preparar_jogadores(locais_dados, numero_jogadores, objetos_territorios):
    jogadores = criar_jogadores(numero_jogadores)
    dividir_territorios(locais_dados, objetos_territorios, jogadores)
    return jogadores

def atualizar_posse_territorios(jogadores):
    for jogador in jogadores:
        for territorio in jogador.territorios:
            territorio.dono = jogador.nome


# exibir os dados para o usuário
def mostrar_territorios(jogador, grupos):
    jogador.organizar_cartas()
    nome_grupo = ""
    bonus_grupo = ""
    for i in jogador.territorios:
        if i.grupo != nome_grupo:
            nome_grupo = i.grupo
            grupo = encontrar_grupo_territorios(nome_grupo=nome_grupo, grupos=grupos)
            bonus_grupo = grupo.exibir_bonus(jogador.nome)
            exibicao_grupo = f"{nome_grupo} {bonus_grupo}"
            print(('-'*40)+"\n"+exibicao_grupo)

        print((f"\t{i.id:02} - {i.nome}").ljust(20,' ')+f"({i.tropas:02})".rjust(5,' '))
    print('-'*40)


def procurar_dono(id, territorios, jogadores):
    nome_dono = territorios[id-1].dono
    return procurar_jogador(nome_dono, jogadores)

def procurar_jogador(nome,jogadores):
    for jogador in jogadores:
        if nome == jogador.nome:
            return jogador

# exibir os dados
def menu_jogador(jogador, grupos):
    cabecalho = jogador.nome.center(40,'-')
    print(cabecalho)
    mostrar_territorios(jogador= jogador, grupos=grupos)
    fim_hud = "FIM FODA"
    print(fim_hud.center(40,'-'))


def main():

    territorios = preparar_territorios(locais_informacoes)
    grupos = criar_grupos_territorios(territorios=territorios, grupos_dados=grupos_informacoes)
    jogadores = preparar_jogadores(locais_dados= locais_informacoes, numero_jogadores= NUMERO_JOGADORES, objetos_territorios=territorios)
    atualizar_posse_territorios(jogadores)

    andamento_partida(jogadores=jogadores, territorios=territorios, grupos=grupos)

main()