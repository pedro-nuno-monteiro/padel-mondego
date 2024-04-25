import psycopg2
import psycopg2.extras
import os
import time
from datetime import datetime, timedelta

def main():
    os.system('cls')

    # conexão com base de dados
    connection = database_connection()
    if not connection:
        print("Erro na conexão - a sair do programa")
        return

    atualiza_campos(connection)

    tipo_user = None
    opcao = 1
    while opcao > 0 or opcao < 3:
        opcao = menu()
        if opcao == 1:

            # encriptar passwords :)
            utilizador = login(connection)

            # definir o tipo de utilizador
            tipo_user = tipo_utilizador(connection, utilizador)
            break

        elif opcao == 2:
            register(connection)

        elif opcao == 3:
            sair()
            break

    if tipo_user == 'admin':
        menu_admin(connection)
    elif tipo_user == 'super_admin':
        menu_super_admin(connection)
    else:
        menu_cliente(connection, utilizador)

    print("adeus")

def menu_cliente(connection, utilizador):

    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    opcao = 1
    while opcao > 0 or opcao < 5:
        opcao = apresentar_menu_cliente()

        if opcao == 1:

            os.system('cls')
            print(" ***** Informações do clube Padel Mondego *****\n *")
            print(" * Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n * Nunc cursus porttitor nisi a venenatis. \n * Mauris elementum tincidunt nisi eu consequat.\n * Cras tristique libero cursus sem eleifend facilisis.\n * In hac habitasse platea dictumst.")
            print(" \n\n ")
            print(" ***** Perfil do Cliente *****\n *")
            print(" * Nome: ", utilizador['nome'])
            print(" * Email: ", utilizador['email'])
            print(" * NIF: ", utilizador['nif'])
            print(" * Telemóvel: ", utilizador['numero_telefone'])
            input(" * \n * Regressar - Enter")

        elif opcao == 2:
            efetuar_reserva(connection, utilizador)

        elif opcao == 3:
            reservas_atuais(connection, utilizador)

        elif opcao == 4:
            historico_reservas(connection, utilizador)

        elif opcao == 5:
            return None

# ------------------------------------
def efetuar_reserva(connection, utilizador):

    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    # update das datas das reservas para teste!
    #custom_date = datetime(year = 2024, month = 4, day = 16)
    #update_query = f"UPDATE reserva SET horario = '{custom_date.strftime('%Y-%m-%d')}'"
    #cursor.execute(update_query)
    #connection.commit()

    date = datetime(year = 2024, month = 4, day = 16) # colocando a hora também conta para o ">="
    fetch_reservas_hoje = """
        SELECT *
        FROM reserva
        WHERE horario >= %s AND (estado = 'Reservado' OR estado = 'Em Espera')
        ORDER BY campo_id_campo, horario, estado DESC
    """

    # executar querys
    cursor.execute(fetch_reservas_hoje, (date,))
    reservas_hoje = cursor.fetchall()
    
    os.system('cls')
    print(" ***** Reserva de campo no Padel Mondego *****\n *")
    #print(" * Campos Disponíveis para hoje,", datetime.now().strftime("%d/%m"))
    print(" * Campos para hoje, 16/04, HORAS (SÓ MOSTRAR A PARTIR DA HORA ATUAL)") # teste
    
    print(" * São as horas que estiverem na atualização! (15h00 = nenhum atualiza)")
    hora_atual = datetime(year = 2024, month = 4, day = 16, hour = 15, minute = 00, second = 00)

    # listar todos os campos e todos os horários
    # estados: reservado; cancelado; finalizado; em espera; em espera cancelado; alterado reservado; alterado finalizado

    # ALTERAR ESTE ARRAY!! ESSA É A SOLUÇÃO!
    horarios_semana = ["15h00", "16h30", "18h00", "19h30", "21h00", "22h30"]
    horarios_fds = ["10h", "11h30", "13h", "14h30", "16h", "17h30", "19h", "20h30"]

    print(" * \n * Campo - 1 * \n * ")
    i = 1
    count_slots_mostrados = 0
    for horario_semana in horarios_semana:
        reservado = False
        # tecnicamente não será necessário este "if" (só apareceram a partir da hora atual)
        #if hora_atual.hour < int(horario_semana[:2]) or (hora_atual.hour == int(horario_semana[:2]) and hora_atual.minute <= int(horario_semana[3:])):
        for reserva_hoje in reservas_hoje:
            if reserva_hoje['campo_id_campo'] == 1 and reserva_hoje['horario'].strftime("%Hh%M") == horario_semana:
                if reserva_hoje['estado'] == 'Reservado':
                    print(" * ", i, " - ", horario_semana, " | Reservado", " | ", reserva_hoje['cliente_utilizador_email'])
                    reservado = True
                    break
        if not reservado:
            print(" * ", i, " - ", horario_semana, " | Livre")
        i += 1
        count_slots_mostrados += 1

    print(" * \n * Campo - 2 * \n * ")
    for horario_semana in horarios_semana:
        reservado = False
        for reserva_hoje in reservas_hoje:
            if reserva_hoje['campo_id_campo'] == 2 and reserva_hoje['horario'].strftime("%Hh%M") == horario_semana:
                if reserva_hoje['estado'] == 'Reservado':
                    print(" * ", i, " - ", horario_semana, " | Reservado", " | ", reserva_hoje['cliente_utilizador_email'])
                    reservado = True
                    break
        if not reservado:
            print(" * ", i, " - ", horario_semana, " | Livre")
        i += 1

    print(" * \n * Campo - 3 * \n * ")
    for horario_semana in horarios_semana:
        reservado = False
        for reserva_hoje in reservas_hoje:
            if reserva_hoje['campo_id_campo'] == 3 and reserva_hoje['horario'].strftime("%Hh%M") == horario_semana:
                if reserva_hoje['estado'] == 'Reservado':
                    print(" * ", i, " - ", horario_semana, " | Reservado", " | ", reserva_hoje['cliente_utilizador_email'])
                    reservado = True
                    break
        if not reservado:
            print(" * ", i, " - ", horario_semana, " | Livre")
        i += 1

    print(" *\n * Outras opções *\n * ")
    print(" * ", i, " - Selecionar outro dia")
    print(" * ", i + 1, " - Regressar")

    # garantir que opção é válida + não reservar um campo que o user tem reservado
    # claro que pode é reservar outros campos que estejam já reservados (ficam Em Espera)
    opcao = 0
    nao_pode_fazer_reserva = False
    regressar = False
    while opcao < 1 or opcao > i + 1 or nao_pode_fazer_reserva:
        opcao = int(input(" *\n * Escolha uma opção -> "))

        campo_escolhido = 0
        # campo 1
        if opcao <= count_slots_mostrados:
            hora_escolhida = horarios_semana[opcao - 1]
            campo_escolhido = 1
        
        # campo 2
        elif opcao > count_slots_mostrados and opcao <= 2 * count_slots_mostrados:
            hora_escolhida = horarios_semana[opcao - 7]
            campo_escolhido = 2

        # campo 3
        elif opcao > 2 * count_slots_mostrados and opcao <= 3 * count_slots_mostrados:
            hora_escolhida = horarios_semana[opcao - 13]
            campo_escolhido = 3
        
        # outro dia
        elif opcao == i:
            efetuar_reserva_outro_dia(connection, utilizador, date)

        # regressar
        elif opcao == i + 1:
            regressar = True
            break
        
        # verificação que não reserva um campo já reservado
        # verificação que não fica em espera para um campo já em espera
        for reserva_hoje in reservas_hoje:
            nao_pode_fazer_reserva = False
            if reserva_hoje['campo_id_campo'] == campo_escolhido and reserva_hoje['horario'].strftime("%Hh%M") == hora_escolhida and reserva_hoje['cliente_utilizador_email'] == utilizador['email'] and reserva_hoje['estado'] == 'Reservado':
                nao_pode_fazer_reserva = True
                print(" * \n * ATENÇÃO -> Não pode reservar um campo que já reservou! * ")
                break
            if reserva_hoje['campo_id_campo'] == campo_escolhido and reserva_hoje['horario'].strftime("%Hh%M") == hora_escolhida and reserva_hoje['cliente_utilizador_email'] != utilizador['email'] and reserva_hoje['estado'] == 'Reservado':
                for res_hoje in reservas_hoje:
                    if res_hoje['horario'].strftime("%Hh%M") == hora_escolhida and res_hoje['cliente_utilizador_email'] == utilizador['email'] and res_hoje['campo_id_campo'] == campo_escolhido and res_hoje['estado'] == 'Em Espera':
                        print(" * \n * ATENÇÃO -> Já está em espera para este campo! * ")
                        nao_pode_fazer_reserva = True
                        break
                if nao_pode_fazer_reserva:
                    break
        
        if opcao < 1 or opcao > i + 1:
            print(" * \n * ATENÇÃO -> Opção inválida! *")

    if not regressar:
    
        # efetuar reserva: "id_reserva, horario, estado, price_id_custo, campo_id_campo, cliente_utilizador_email"
        reserva_a_efetuar = []
        
        # basta modificar o tipo do PK para autoincremento
        fetch_maior_id = """
            SELECT MAX(id_reserva)
            FROM reserva
        """
        cursor.execute(fetch_maior_id)
        ultimo_id = cursor.fetchone()[0]

        # último id
        reserva_a_efetuar.append(ultimo_id + 1)

        # hora escolhida
        hora_escolhida = datetime.strptime(hora_escolhida, "%Hh%M")
        # colocar a data de teste -> 16/04
        hora_escolhida = hora_escolhida.replace(year = 2024, month = 4, day = 16)
        
        reserva_a_efetuar.append(hora_escolhida)
        
        # estado (Reservado ou Em Espera)
        estado = "Reservado"
        for reserva_hoje in reservas_hoje:
            if reserva_hoje['horario'] == hora_escolhida and reserva_hoje['cliente_utilizador_email'] != utilizador['email'] and reserva_hoje['campo_id_campo'] == campo_escolhido:
                estado = "Em Espera"

        reserva_a_efetuar.append(estado)
        
        # custo
        tipo_dia = "Dia de semana"
        tipo_horario = "Normal"
        if hora_escolhida.isoweekday() >= 6:
            tipo_dia = "Fim de semana"
        if hora_escolhida.hour >= 18 and tipo_dia == "Dia de semana":
            tipo_horario = "Nobre"
        
        buscar_lista_preco = """
            SELECT id_custo, preco_atual
            FROM price 
            WHERE ativo = True AND tipo_dia = %s AND horario = %s
        """
        cursor.execute(buscar_lista_preco, (tipo_dia, tipo_horario))
        linha = cursor.fetchone()
        id_custo = linha[0]
        preco_reserva = linha[1]

        reserva_a_efetuar.append(id_custo)

        reserva_a_efetuar.append(campo_escolhido)

        reserva_a_efetuar.append(utilizador['email'])

        if estado == "Em Espera":
            print(" * Ficará em espera para o slot: ", hora_escolhida.strftime("%d/%m"), " | ", hora_escolhida.strftime("%Hh%M"), " | Campo -", campo_escolhido)
        else:
            print(" * A seguinte reserva será efetuada: ", hora_escolhida.strftime("%d/%m"), " | ", hora_escolhida.strftime("%Hh%M"), " | ", preco_reserva, "€ | Campo -", campo_escolhido)

        efetua_reserva = "INSERT INTO reserva VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(efetua_reserva, reserva_a_efetuar)
        connection.commit()

        print(" * \n * Reserva efetuada com sucesso! * ")
        input(" * \n * Regressar - Enter")

# ------------------------------------
def efetuar_reserva_outro_dia(connection, utilizador, date):

    os.system('cls')
    print(" ***** Reserva de campo no Padel Mondego *****\n *")
    print(" * Selecione o dia que quer reservar *\n * ")
    
    # subsituir por dia atual
    # e corrigir o facto de mudar de mês :/
    dia = date.day
    for j in range(dia, dia + 7):
        print(" * ", j , " - ", date.replace(day = j).strftime("%d/%m"))
    
    print(" * \n * ", j + 1, " - Regressar")

    opcao = 0
    while opcao < 1 or opcao > j + 1:
        opcao = int(input(" * Escolha uma opção -> "))

        if opcao == j + 1:
            break
        else:
            dia_escolhido = opcao + dia
            break
    print(" * \n * Dia escolhido -> ", dia_escolhido, "\n * ")
    input(" * \n * Regressar - Enter")
    
# ------------------------------------
def reservas_atuais(connection, utilizador):

    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    # mostra reservas futuras
    fetch_reservas_user = """
        SELECT *
        FROM reserva
        WHERE cliente_utilizador_email = %s
        ORDER BY campo_id_campo, horario
    """

    cursor.execute(fetch_reservas_user, (utilizador['email'],))
    reservas_futuras = cursor.fetchall()

    os.system('cls')
    print(" ***** Reservas Futuras - Padel Mondego *****\n *")
    print(" * Neste menu é possível:")
    print(" * * Consultar as reservas atuais")
    print(" * * Cancelar uma reserva (escolher)")
    print(" * * Consultar reservas em espera\n *")
    
    i = 1
    for reserva_futura in reservas_futuras:
        if reserva_futura['estado'] == "Reservado":
            print(f" * {i}. Campo - {reserva_futura['campo_id_campo']} * ")
            i += 1

        else:
            print(f" * *  Campo - {reserva_futura['campo_id_campo']} * ")
            
        buscar_preco = """
            SELECT preco_atual
            FROM price 
            WHERE id_custo = %s 
        """
        cursor.execute(buscar_preco, (reserva_futura['price_id_custo'],))
        preco = cursor.fetchone()[0]

        print(" *   ", reserva_futura['horario'].strftime("%d/%m"), ", ", reserva_futura['horario'].strftime("%Hh%M"), " | ", preco, "€ | ", reserva_futura['estado'], "\n *")

    print(f" * {i}. Regressar")

    opcao = 0
    while opcao < 1 or opcao > i + 1:
        opcao = int(input(" * \n * Escolha uma opção -> "))

        if opcao == i:
            break
        
        id_reserva_cancelar = reservas_futuras[opcao - 1]['id_reserva']

        # estado fica "Cancelado"
        cancelar_reserva = """
            UPDATE reserva
            SET estado = 'Cancelado'
            WHERE id_reserva = %s
        """
        cursor.execute(cancelar_reserva, (id_reserva_cancelar,))
        connection.commit()

        print(" * Reserva cancelada com sucesso!")

        input(" * \n * Regressar - Enter")

# ------------------------------------
def historico_reservas(connection, utilizador):
    
    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    # hora atual teste -> 18h00
    horario_atual = datetime(year = 2024, month = 4, day = 16, hour = 18, minute = 00, second = 00)

    fetch_historico_reservas = """
        SELECT horario, estado, price_id_custo, campo_id_campo, cliente_utilizador_email
        FROM reserva
        WHERE cliente_utilizador_email = %s AND horario < %s
        ORDER BY horario, campo_id_campo
    """
    cursor.execute(fetch_historico_reservas, [(utilizador['email'],), horario_atual])
    linhas = cursor.fetchall()

    os.system('cls')
    print(" ***** Hisórico de Reservas - Padel Mondego *****\n *")

    for linha in linhas:
        print(" *  Campo", linha['campo_id_campo'], "- ", linha['horario'].strftime("%d/%m"), " * ")

        buscar_preco = """
            SELECT preco_atual
            FROM price 
            WHERE id_custo = %s 
        """
        cursor.execute(buscar_preco, (linha['price_id_custo'],))
        preco = cursor.fetchone()[0]

        print(" * ", linha['horario'].strftime("%Hh%M"), " | ", preco, "€", " | ", linha['estado'], "\n *")

    input(" * \n * Regressar - Enter")

# ------------------------------------
# retorna "super_admin", "admin" ou "cliente"
def tipo_utilizador(connection, utilizador):

    tipo_user = None

    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    # definir linhas de sql querys
    fetch_admins = """
        SELECT *
        FROM utilizador as u, administrador as a
        WHERE u.email = a.utilizador_email AND u.email = %s
    """

    # executar querys
    cursor.execute(fetch_admins, (utilizador['email'],))
    linha = cursor.fetchone()

    if linha is not None:
        if linha['super_admin']:
            tipo_user = 'super_admin'
        else:
            tipo_user = 'admin'
    else:
        tipo_user = 'cliente'

    return tipo_user

def login(connection):

    os.system('cls')

    print(" ***** Login *****")
    print(" * \n * Login com os seus dados\n *")

    email_invalido = True
    passe_invalida = True

    while email_invalido or passe_invalida:

        email = str(123)
        while email.isdigit():
            email = input(" * Email: ")
            if email.isdigit():
                print("\n *** ATENÇÃO -> Input inválido ***")

        passe = str(123)
        while passe.isdigit():
            passe = input(" * Password: ")
            if passe.isdigit():
                print("\n *** ATENÇÃO -> Input inválido! ***")

        # fetch de utilizadores
        cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)
        fetch_utilizadores = " SELECT email, passe, nome FROM utilizador WHERE email = %s"
        cursor.execute(fetch_utilizadores, (email,))
        linha = cursor.fetchone()

        # verificar se o utilizador existe
        utilizador = []
        if linha is None:
            email_invalido = True
            passe_invalida = True

        elif email == linha['email']:
            email_invalido = False

            if passe == linha['passe']:
                passe_invalida = False
                nome = linha['nome']
                utilizador = {'email': email, 'passe': passe, 'nome': nome}
            else:
                passe_invalida = True

        if email_invalido or passe_invalida:
            print(" * \n *** ATENÇÃO -> Um dos campos está inválido! ***")

    print(" * \n * \n * Login efetuado com sucesso! * ")

    # verifica se é admin ou cliente
    tipo_user = tipo_utilizador(connection, utilizador)

    if tipo_user == 'admin':
        utilizador['super_admin'] = False
        tipo_user = "Admin"
    elif tipo_user == 'super_admin':
        utilizador['super_admin'] = True
        tipo_user = "Super Admin"
    elif tipo_user == 'cliente':
        fetch_utilizadores = " SELECT nif, numero_telefone FROM cliente WHERE utilizador_email = %s"
        cursor.execute(fetch_utilizadores, (email,))
        nif, numero_telefone = cursor.fetchone()
        utilizador.update({'nif': nif, 'numero_telefone': numero_telefone})
        tipo_user = "Cliente"
    else:
        print("Erro na função de login!")
        raise Exception("Erro na função de login!")

    print(" * \n * Bem vindo,", tipo_user, nome)
    time.sleep(1)
    return utilizador

def register(connection):
    os.system('cls')

    user = []

    print(" ***** Registar *****")
    print(" * \n * Registe os seus dados\n *")

    # adicionar whiles de segurança
    nome = input(" * Nome: ")

    email_existe = True
    while email_existe:
        email = input(" * Email: ")

        # verificar se o email/nome já existe
        cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

        fetch_utilizadores = """
            SELECT nome, email, passe
            FROM utilizador
        """

        cursor.execute(fetch_utilizadores)
        linhas = cursor.fetchall()

        for linha in linhas:
            if email == linha['email']:
                email_existe = True
                print(" * \n *** ATENÇÃO -> Email já registado! ***")
                break
            else:
                email_existe = False

    password = input(" * Password: ")

    # tem de ser por esta ordem!
    user.append(email)
    user.append(password)
    user.append(nome)

    # insere utilizador (antes de inserir admin ou cliente)
    cursor = connection.cursor()
    insere_user = "INSERT INTO utilizador VALUES (%s, %s, %s)"
    cursor.execute(insere_user, user)
    connection.commit()

    print(" * \n * \n * Tipo de utilizador\n *")
    print(" * 1 - Admin")
    print(" * 2 - Cliente\n * ")

    tipo = int(input(" * Escolha uma opção -> "))

    if tipo == 1:

        user_admin = []

        # fetch último admin_id
        cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

        fetch_restantes_admins = """
            SELECT a.admin_id
            FROM administrador as a
            ORDER BY a.admin_id DESC
        """

        cursor.execute(fetch_restantes_admins)
        linha = cursor.fetchone()
        ultimo_admin_id, = linha

        # atribuir características de admin
        user_admin.append(ultimo_admin_id + 1)
        print(" * \n * ")
        print(" * Super Admin\n * ")
        print(" * 1 - Sim")
        print(" * 0 - Não\n * ")
        sa = int(input(" * Escolha uma opção -> "))

        if sa:
            user_admin.append(True)
        else:
            user_admin.append(False)

        user_admin.append(email)

        # inserir utilizador + admin
        cursor = connection.cursor()

        print(" * \n * \n * Registo efetuado com os dados acima indicados! * ")

        insere_admin = "INSERT INTO administrador VALUES (%s, %s, %s)"

        cursor.execute(insere_admin, user_admin)
        connection.commit()

        user.append(user_admin)

    else:
        user_cliente = []

        print(" * \n * ")
        nif = str(9999999999)
        while len(nif) > 9 or not nif.isdigit():
            nif = input(" * NIF: ")
            if len(nif) > 9 or not nif.isdigit():
                print("\n *** ATENÇÃO -> NIF inválido! ***")

        telemovel = str(9999999999)
        while len(telemovel) > 9 or not telemovel.isdigit():
            telemovel = input(" * Telemóvel: ")
            if len(telemovel) > 9 or not telemovel.isdigit():
                print("\n *** ATENÇÃO -> Telemóvel inválido! ***")

        user_cliente.append(nif)
        user_cliente.append(telemovel)
        user_cliente.append(email)

        # inserir utilizador + cliente
        cursor = connection.cursor()

        print(" * \n * \n * Registo efetuado com os dados acima indicados! * ")

        insere_admin = "INSERT INTO cliente VALUES (%s, %s, %s)"

        cursor.execute(insere_admin, user_cliente)
        connection.commit()

        user.append(user_cliente)

    time.sleep(2)
    os.system('cls')
    return user

# ------------------------------------
def sair():
    print("a sair do programa...")
    return None

# ------------------------------------
def apresentar_menu_cliente():
    os.system('cls')
    print(" ***** Menu Cliente *****\n *")
    print(" * 1 - Informações e Perfil")
    print(" * 2 - Reservar Campo")
    print(" * 3 - Reservas atuais")
    print(" * 4 - Histórico de Reservas")
    print(" * 5 - Logout | Sair\n *")

    opcao = 0
    while opcao < 1 or opcao > 5:
        opcao = int(input(" * Escolha uma opção -> "))

    return opcao

# ------------------------------------
def menu():

    print(" ***** Padel Mondego *****\n")
    print(" * Bem Vindo à mais recente aplicação de reservas de campos de Padel")
    print(" * ")
    print(" * 1 - Login")
    print(" * 2 - Registar")
    print(" * 3 - Sair\n * ")

    opcao = 0
    while opcao < 1 or opcao > 3:
        opcao = int(input(" * Escolha uma opção -> "))

    return opcao

# ------------------------------------
def atualiza_campos(connection):

    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    # recebe hora atual
    # current_datetime = datetime.now()

    current_datetime = datetime(year = 2024, month = 4, day = 16, hour = 14, minute = 00, second = 00)
    diferenca = current_datetime - timedelta(hours = 1, minutes = 30)

    # dar update das reservas em que já passou 1h30
    # imaginemos -> jogo das 15h e são 16h50
    # 16h50 - 1h30 = 15h20; logo, horario (15h) < 15h20 
    update_jogos_a_decorrer = """
        UPDATE reserva
        SET estado = 'Finalizado'
        WHERE estado = 'Reservado' AND horario < %s
    """

    cursor.execute(update_jogos_a_decorrer, (diferenca,))
    connection.commit()

    if cursor.rowcount > 0:
        print("Fields updated successfully\n\n")
    else:
        print("\n")

# ------------------------------------
def database_connection():
    print("Conexão com base de dados")

    try:
        connection = psycopg2.connect(
            user = "postgres",
            password = "pepas1206",
            host = "127.0.0.1",
            port = "5432",
            database = "padel mondego"
        )

        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record)
        return connection

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return None

# ------------------------------------
if __name__ == '__main__':
    main()