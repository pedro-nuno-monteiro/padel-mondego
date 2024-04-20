import psycopg2
import psycopg2.extras
import os
import time
from datetime import datetime

def main():
    os.system('cls')

    # conexão com base de dados
    connection = database_connection()
    if not connection:
        print("Erro na conexão - a sair do programa")
        return

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

    os.system('cls')
    print(" ***** Menu Cliente *****\n *")
    print(" * 1 - Informações e Perfil")
    print(" * 2 - Reservar Campo")
    print(" * 3 - Reservas atuais")
    print(" * 4 - Histórico de Reservas")
    print(" * 5 - Logout\n *")

    opcao = 1
    while opcao > 0 or opcao < 6:
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

            # update das datas das reservas para teste!
            #custom_date = datetime(year = 2024, month = 4, day = 16)
            #update_query = f"UPDATE reserva SET horario = '{custom_date.strftime('%Y-%m-%d')}'"
            #cursor.execute(update_query)
            #connection.commit()

            fetch_reservas = """
                SELECT *
                FROM reserva as r
            """

            # executar querys
            cursor.execute(fetch_reservas)
            linhas = cursor.fetchall()

            # colocar as reservas do dia atual (teste = 16/04)
            reservas_hoje = []
            ultimo_id = 0
            date = datetime(year = 2024, month = 4, day = 16)
            for linha in linhas:
                ultimo_id += 1
                if linha['horario'].date() == date.date():
                    reservas_hoje.append(linha)

                # funcional
                #if linha['horario'].strftime("%Y-%m-%d") == datetime.now().strftime("%Y-%m-%d"):
                #    reservas_hoje.append(linha)

            os.system('cls')
            print(" ***** Reserva de campo no Padel Mondego *****\n *")
            #print(" * Campos Disponíveis para hoje,", datetime.now().strftime("%d/%m"))
            print(" * Campos para hoje, 16/04, HORAS (SÓ MOSTRAR A PARTIR DA HORA ATUAL)") # teste

            # listar todos os campos e todos os horários
            # estados: reservado; cancelado; finalizado; em espera; em espera cancelado; alterado reservado; alterado finalizado
            horarios_semana = ["15h00", "16h30", "18h00", "19h30", "21h00", "22h30"]
            horarios_fds = ["10h", "11h30", "13h", "14h30", "16h", "17h30", "19h", "20h30"]

            print(" * \n * Campo - 1 * \n * ")
            i = 1
            for horario_semana in horarios_semana:
                reservado = False
                for reserva_hoje in reservas_hoje:
                    if reserva_hoje['campo_id_campo'] == 1 and reserva_hoje['horario'].strftime("%Hh%M") == horario_semana:
                        if reserva_hoje['estado'] == 'Reservado':
                            print(" * ", i, " - ", horario_semana, " | Reservado", " | ", reserva_hoje['cliente_utilizador_email'])
                            reservado = True
                            break
                if not reservado:
                    print(" * ", i, " - ", horario_semana, " | Livre")
                i += 1

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

                if opcao <= 6:
                    hora_escolhida = horarios_semana[opcao - 1]
                elif opcao > 6 and opcao <= 12:
                    hora_escolhida = horarios_semana[opcao - 7]
                elif opcao > 12 and opcao <= 18:
                    hora_escolhida = horarios_semana[opcao - 13]

                elif opcao == i:
                    # vai para menu que pergunta que dia
                    print("oh diabooooo")
                    regressar = True # para enquanto não estiver implementado
                    break
                elif opcao == i + 1:
                    print("regressar")
                    regressar = True
                    break

                for reserva_hoje in reservas_hoje:
                    if reserva_hoje['estado'] == 'Reservado' and reserva_hoje['horario'].strftime("%Hh%M") == hora_escolhida and reserva_hoje['cliente_utilizador_email'] == utilizador['email']:
                        nao_pode_fazer_reserva = True
                        print(" * \n * ATENÇÃO -> Não pode reservar um campo que já reservou! * ")
                        break

                # USER SÓ PODE FICAR EM ESPERA 1 VEZ

            if not regressar:
                # efetuar reserva
                reserva_a_efetuar = []
                
                # último id
                reserva_a_efetuar.append(ultimo_id + 1)

                # hora escolhida
                campo_escolhido = 0
                if opcao <= 6:
                    campo_escolhido = 1
                    hora_escolhida = horarios_semana[opcao - 1]
                elif opcao > 6 and opcao <= 12:
                    campo_escolhido = 2
                    hora_escolhida = horarios_semana[opcao - 7]
                elif opcao > 12 and opcao <= 18:
                    campo_escolhido = 3
                    hora_escolhida = horarios_semana[opcao - 13]

                hora_escolhida = datetime.strptime(hora_escolhida, "%Hh%M")
                # colocar a data de teste -> 16/04
                hora_escolhida = hora_escolhida.replace(year = 2024, month = 4, day = 16)
                
                reserva_a_efetuar.append(hora_escolhida)
                
                # ver outros casos
                estado = "Reservado"
                for linha in linhas:
                    if linha['estado'] == "Reservado" and linha['horario'] == hora_escolhida and linha['cliente_utilizador_email'] != utilizador['email'] and linha['campo_id_campo'] == campo_escolhido:
                        estado = "Em Espera"

                reserva_a_efetuar.append(estado)
                
                # determinar custo
                tipo_dia = "Dia de semana"
                tipo_horario = "Normal"
                if hora_escolhida.isoweekday() >= 6:
                    tipo_dia = "Fim de semana"
                if hora_escolhida.hour >= 18 and tipo_dia == "Dia de semana":
                    tipo_horario = "Nobre"
                
                buscar_lista_preco = """
                    SELECT id_custo
                    FROM price 
                    WHERE ativo = True AND tipo_dia = %s AND horario = %s 
                """
                cursor.execute(buscar_lista_preco, (tipo_dia, tipo_horario))
                id_custo = cursor.fetchone()[0]

                reserva_a_efetuar.append(id_custo)

                reserva_a_efetuar.append(campo_escolhido)

                reserva_a_efetuar.append(utilizador['email'])

                print(" * A seguinte reserva será efetuada: ", reserva_a_efetuar)

                efetua_reserva = "INSERT INTO reserva VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(efetua_reserva, reserva_a_efetuar)
                connection.commit()

                print(" * \n * Reserva efetuada com sucesso! * ")
                input(" * \n * Regressar - Enter")

        elif opcao == 3:
            # mostra reservas futuras

            fetch_reservas_user = """
                SELECT horario, estado, price_id_custo, campo_id_campo
                FROM reserva
                WHERE cliente_utilizador_email = %s
                ORDER BY campo_id_campo, horario
            """

            cursor.execute(fetch_reservas_user, (utilizador['email'],))
            linhas = cursor.fetchall()

            os.system('cls')
            print(" ***** Reservas Futuras - Padel Mondego *****\n *")
            
            for linha in linhas:
                print(" * Campo - ", linha['campo_id_campo'], " * ")

                buscar_preco = """
                    SELECT preco_atual
                    FROM price 
                    WHERE id_custo = %s 
                """
                cursor.execute(buscar_preco, (linha['price_id_custo'],))
                preco = cursor.fetchone()[0]

                print(" * ", linha['horario'].strftime("%d/%m"), " | ", linha['horario'].strftime("%Hh%M"), " | ", preco, "€ | ", linha['estado'], "\n *")

            input(" * \n * Regressar - Enter")

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
        nif = str(9999999)
        while len(nif) >= 7 or not nif.isdigit():
            nif = input(" * NIF: ")
            if len(nif) >= 7 or not nif.isdigit():
                print("\n *** ATENÇÃO -> NIF inválido! ***")

        telemovel = str(9999999)
        while len(telemovel) >= 7 or not telemovel.isdigit():
            telemovel = input(" * Telemóvel: ")
            if len(telemovel) >= 7 or not telemovel.isdigit():
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
    print(" * 5 - Logout\n *")

    opcao = 0
    while opcao < 1 or opcao > 5:
        opcao = int(input(" * Escolha uma opção -> "))

    return opcao

# ------------------------------------
def menu():

    print("***** Padel Mondego *****\n")
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
        print("You are connected to - ", record, "\n")
        return connection

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return None

# ------------------------------------
if __name__ == '__main__':
    main()