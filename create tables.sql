CREATE TABLE cliente (
	nif		 NUMERIC(8,2),
	numero_telefone	 NUMERIC(8,2),
	utilizador_email VARCHAR(512),
	PRIMARY KEY(utilizador_email)
);

CREATE TABLE reserva (
	id_reserva		 NUMERIC(8,2),
	horario			 TIMESTAMP,
	estado			 TEXT,
	price_id_custo		 BIGINT NOT NULL,
	campo_id_campo		 BIGINT NOT NULL,
	cliente_utilizador_email VARCHAR(512) NOT NULL,
	PRIMARY KEY(id_reserva)
);

CREATE TABLE mensagem (
	id_mensagem			 NUMERIC(8,2),
	assunto			 TEXT,
	conteudo			 TEXT,
	data_envio			 DATE,
	administrador_utilizador_email VARCHAR(512) NOT NULL,
	PRIMARY KEY(id_mensagem)
);

CREATE TABLE administrador (
	admin_id	 NUMERIC(8,2),
	super_admin	 BOOL,
	utilizador_email VARCHAR(512),
	PRIMARY KEY(utilizador_email)
);

CREATE TABLE utilizador (
	email VARCHAR(512),
	passe VARCHAR(512),
	nome	 VARCHAR(512),
	PRIMARY KEY(email)
);

CREATE TABLE permissoes (
	alterar_preco	 BOOL,
	alterar_reserva	 BOOL,
	cancelar_reserva BOOL,
	conceder_cliente BOOL,
	remover_cliente	 BOOL
);

CREATE TABLE campo (
	id_campo	 BIGINT,
	descricao VARCHAR(512),
	PRIMARY KEY(id_campo)
);

CREATE TABLE price (
	id_custo	 BIGINT,
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
	mensagem_id_mensagem	 NUMERIC(8,2),
	cliente_utilizador_email VARCHAR(512),
	PRIMARY KEY(mensagem_id_mensagem,cliente_utilizador_email)
);

CREATE TABLE administrador_permissoes (
	administrador_utilizador_email VARCHAR(512),
	PRIMARY KEY(administrador_utilizador_email)
);

ALTER TABLE cliente ADD CONSTRAINT cliente_fk1 FOREIGN KEY (utilizador_email) REFERENCES utilizador(email);
ALTER TABLE reserva ADD CONSTRAINT reserva_fk1 FOREIGN KEY (price_id_custo) REFERENCES price(id_custo);
ALTER TABLE reserva ADD CONSTRAINT reserva_fk2 FOREIGN KEY (campo_id_campo) REFERENCES campo(id_campo);
ALTER TABLE reserva ADD CONSTRAINT reserva_fk3 FOREIGN KEY (cliente_utilizador_email) REFERENCES cliente(utilizador_email);
ALTER TABLE mensagem ADD CONSTRAINT mensagem_fk1 FOREIGN KEY (administrador_utilizador_email) REFERENCES administrador(utilizador_email);
ALTER TABLE administrador ADD CONSTRAINT administrador_fk1 FOREIGN KEY (utilizador_email) REFERENCES utilizador(email);
ALTER TABLE mensagem_cliente ADD CONSTRAINT mensagem_cliente_fk1 FOREIGN KEY (mensagem_id_mensagem) REFERENCES mensagem(id_mensagem);
ALTER TABLE mensagem_cliente ADD CONSTRAINT mensagem_cliente_fk2 FOREIGN KEY (cliente_utilizador_email) REFERENCES cliente(utilizador_email);
ALTER TABLE administrador_permissoes ADD CONSTRAINT administrador_permissoes_fk1 FOREIGN KEY (administrador_utilizador_email) REFERENCES administrador(utilizador_email);
