import psycopg2
import psycopg2.extras
import os
import time


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
    
    opcao = 0
    while opcao < 1 or opcao > 5:
        opcao = int(input(" * Escolha uma opção -> "))

    if opcao == 1:

        # definir linhas de sql querys
        fetch_utilizadores = """
            SELECT *
            FROM utilizador as u, administrador as a
            WHERE u.email = a.utilizador_email AND u.email = %s
        """

        # executar querys
        cursor.execute(fetch_utilizadores, (utilizador['email'],))
        linha = cursor.fetchone()

        os.system('cls')
        print(" ***** Informações do clube Padel Mondego *****\n *")
        print("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc cursus porttitor nisi a venenatis. Mauris elementum tincidunt nisi eu consequat. Cras tristique libero cursus sem eleifend facilisis. In hac habitasse platea dictumst. Mauris fringilla viverra elit, sit amet viverra ligula ultricies ut. Mauris sagittis dictum vestibulum.")
        print(" \n\n\n ")
        print(" ***** Perfil do Cliente *****\n *")
        print(" * Nome: ", utilizador['nome'])
        print(" * Email: ", utilizador['email'])
        print(" * NIF: ", utilizador['nif'])
        print(" * Telemóvel: ", utilizador['numero_telefone'])
        

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
        fetch_utilizadores = " SELECT super_admin FROM administrador WHERE utilizador_email = %s"
        cursor.execute(fetch_utilizadores, (email,))
        linha = cursor.fetchone()
        if linha['super_admin']:
            utilizador['super_admin'] = True
        else:
            utilizador['super_admin'] = False
    else:
        fetch_utilizadores = " SELECT nif, numero_telefone FROM cliente WHERE utilizador_email = %s"
        cursor.execute(fetch_utilizadores, (email,))
        nif, numero_telefone = cursor.fetchone()
        utilizador.update({'nif': nif, 'numero_telefone': numero_telefone})
    
    print(" * \n * Bem vindo,", tipo_user, nome)
    time.sleep(2)
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

def sair():
    print("a sair do programa...")
    return None

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