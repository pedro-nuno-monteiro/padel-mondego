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

    opcao = menu()

    print(opcao)
    if opcao == 1:
        login()
    elif opcao == 2:
        register(connection)
    else:
        sair()

    time.sleep(5)
    
    # definir o tipo de utilizador
    utilizadores_admin = tipo_utilizador(connection)

    admins = []
    s_admin = []
    for user in utilizadores_admin:
        if user['super_admin']:
            s_admin.append(user)
        else:
            admins.append(user)

    print("Admins: ", admins)
    print("Super Admins: ", s_admin)


def tipo_utilizador(connection):
    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    # definir linhas de sql querys
    fetch_admins = """
        SELECT u.email, u.nome, u.passe, a.admin_id, a.super_admin
        FROM utilizador as u, administrador as a
        WHERE u.email = a.utilizador_email
    """

    # executar querys
    cursor.execute(fetch_admins)
    rows = cursor.fetchall()
    return rows

def login():

    return None

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