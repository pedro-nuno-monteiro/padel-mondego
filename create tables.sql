CREATE EXTENSION pgcrypto;

-- sequência
CREATE SEQUENCE reserva_id_reserva_seq START WITH 9;
CREATE SEQUENCE price_id_custo_seq START WITH 5;
CREATE SEQUENCE mensagem_id_mensagem_seq START WITH 4;

CREATE TABLE cliente (
	nif		 NUMERIC(9,0),
	numero_telefone	 NUMERIC(9,0),
	utilizador_email VARCHAR(512),
	PRIMARY KEY(utilizador_email),
	CONSTRAINT valid_nif CHECK (nif >= 100000000 AND nif <= 999999999),
    CONSTRAINT valid_numero_telefone CHECK (numero_telefone >= 100000000 AND numero_telefone <= 999999999)
);

CREATE TABLE reserva (
	id_reserva		 SERIAL,
	horario			 TIMESTAMP,
	estado			 TEXT,
	price_id_custo		 INTEGER NOT NULL,
	campo_id_campo		 INTEGER NOT NULL,
	cliente_utilizador_email VARCHAR(512) NOT NULL,
	PRIMARY KEY(id_reserva)
);

CREATE TABLE mensagem (
	id_mensagem			 SERIAL,
	assunto			 TEXT,
	conteudo			 TEXT,
	data_envio			 DATE,
	geral				 BOOL,
	administrador_utilizador_email VARCHAR(512) NOT NULL,
	PRIMARY KEY(id_mensagem)
);

CREATE TABLE administrador (
	super_admin	 BOOL,
	utilizador_email VARCHAR(512),
	PRIMARY KEY(utilizador_email)
);

CREATE TABLE utilizador (
	email VARCHAR(512),
	passe VARCHAR(512),
	nome	 VARCHAR(512),
	PRIMARY KEY(email),
	CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

CREATE TABLE campo (
	id_campo	 INTEGER,
	descricao VARCHAR(512),
	PRIMARY KEY(id_campo)
);

CREATE TABLE price (
	id_custo	 SERIAL,
	tipo_dia	 VARCHAR(512),
	horario	 VARCHAR(512),
	data_alteracao DATE,
	ativo		 BOOL,
	valor_antigo	 NUMERIC(8,2),
	preco_atual	 NUMERIC(8,2),
	PRIMARY KEY(id_custo)
);

CREATE TABLE mensagem_cliente (
	lida			 BOOL,
	mensagem_id_mensagem	 INTEGER,
	cliente_utilizador_email VARCHAR(512),
	PRIMARY KEY(mensagem_id_mensagem,cliente_utilizador_email)
);


ALTER TABLE cliente ADD UNIQUE (nif, numero_telefone);
ALTER TABLE cliente ADD CONSTRAINT cliente_fk1 FOREIGN KEY (utilizador_email) REFERENCES utilizador(email);
ALTER TABLE reserva ADD CONSTRAINT reserva_fk1 FOREIGN KEY (price_id_custo) REFERENCES price(id_custo);
ALTER TABLE reserva ADD CONSTRAINT reserva_fk2 FOREIGN KEY (campo_id_campo) REFERENCES campo(id_campo);
ALTER TABLE reserva ADD CONSTRAINT reserva_fk3 FOREIGN KEY (cliente_utilizador_email) REFERENCES cliente(utilizador_email);
ALTER TABLE mensagem ADD CONSTRAINT mensagem_fk1 FOREIGN KEY (administrador_utilizador_email) REFERENCES administrador(utilizador_email);
ALTER TABLE administrador ADD CONSTRAINT administrador_fk1 FOREIGN KEY (utilizador_email) REFERENCES utilizador(email);
ALTER TABLE mensagem_cliente ADD CONSTRAINT mensagem_cliente_fk1 FOREIGN KEY (mensagem_id_mensagem) REFERENCES mensagem(id_mensagem);
ALTER TABLE mensagem_cliente ADD CONSTRAINT mensagem_cliente_fk2 FOREIGN KEY (cliente_utilizador_email) REFERENCES cliente(utilizador_email);

-- trigger
CREATE OR REPLACE FUNCTION jogo_reservado_termina()
RETURNS trigger AS $$
BEGIN
	IF OLD.estado = 'Reservado' AND NEW.estado = 'Finalizado' THEN
		UPDATE reserva
		SET estado = 'Em Espera Cancelado'
		WHERE estado = 'Em Espera'
		AND campo_id_campo = OLD.campo_id_campo 
		AND horario = OLD.horario;
    END IF;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_estado_em_espera_trigger
AFTER UPDATE ON reserva
FOR EACH ROW
EXECUTE FUNCTION jogo_reservado_termina();