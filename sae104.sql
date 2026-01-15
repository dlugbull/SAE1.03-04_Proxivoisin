# Martins Cristiano
# Mahamane Mansourah
# Lugbull Damien

DROP TABLE IF EXISTS note;
DROP TABLE IF EXISTS est_passager;
DROP TABLE IF EXISTS trajet;
DROP TABLE IF EXISTS voiture;
DROP TABLE IF EXISTS lieu;
DROP TABLE IF EXISTS personne;
DROP TABLE IF EXISTS modele;
DROP TABLE IF EXISTS ville;
DROP TABLE IF EXISTS sexe;
DROP TABLE IF EXISTS type_voiture;
DROP TABLE IF EXISTS marque;


CREATE TABLE marque(
    id_marque INT AUTO_INCREMENT,
    nom_marque VARCHAR(255),
    PRIMARY KEY(id_marque)
);

CREATE TABLE type_voiture(
    id_type INT AUTO_INCREMENT,
    nom_type_voiture VARCHAR(255),
    PRIMARY KEY(id_type)
);

CREATE TABLE sexe(
    id_sexe INT AUTO_INCREMENT,
    nom_sexe VARCHAR(1),
    PRIMARY KEY(id_sexe)
);

CREATE TABLE ville(
    id_ville INT AUTO_INCREMENT,
    code_postal VARCHAR(50),
    nom_ville VARCHAR(255),
    PRIMARY KEY(id_ville)
);

CREATE TABLE modele(
    id_modele INT AUTO_INCREMENT,
    nom_modele VARCHAR(50),
    marque_id INT NOT NULL,
    PRIMARY KEY(id_modele),
    CONSTRAINT modele_marque
    FOREIGN KEY(marque_id) REFERENCES marque(id_marque)
);

CREATE TABLE personne(
    id_personne INT AUTO_INCREMENT,
    nom_personne VARCHAR(50),
    prenom VARCHAR(50),
    date_naissance DATE,
    adresse VARCHAR(255),
    telephone VARCHAR(10),
    mail VARCHAR(255),
    sexe_id INT NOT NULL,
    PRIMARY KEY(id_personne),
    CONSTRAINT personne_sexe
       FOREIGN KEY(sexe_id) REFERENCES sexe(id_sexe)
);

CREATE TABLE lieu(
    id_lieu INT AUTO_INCREMENT,
    nom_lieu VARCHAR(255),
    adresse VARCHAR(255),
    ville_id INT NOT NULL,
    altitude NUMERIC,
    capacite_parking INT,
    cout_stationnement NUMERIC(5,2),
    places_PMR INT,
    PRIMARY KEY(id_lieu),
    CONSTRAINT lieu_ville
       FOREIGN KEY(ville_id) REFERENCES ville(id_ville)
);

CREATE TABLE voiture(
   immatriculation VARCHAR(50),
   modele_id INT NOT NULL,
   personne_id INT NOT NULL,
   type_id INT NOT NULL,
   couleur VARCHAR(30),
   numero_assurance VARCHAR(50),
   cout_assurance DECIMAL(10,2),
   date_derniere_revision DATE,
   statut ENUM('active', 'en entretien', 'hors service', 'en pause'),
   type_carburant ENUM('essence', 'diesel', 'électrique', 'hybride'),
   kilometrage INT,
   nombre_places INT CHECK(nombre_places BETWEEN 2 AND 9),
   disponibilite BOOLEAN,
   PRIMARY KEY(immatriculation),
   FOREIGN KEY(modele_id) REFERENCES modele(id_modele),
   FOREIGN KEY(personne_id) REFERENCES personne(id_personne),
   FOREIGN KEY(type_id) REFERENCES type_voiture(id_type)
);

CREATE TABLE trajet(
    id_trajet INT AUTO_INCREMENT,
    date_trajet DATE,
    heure_depart TIME,
    distance INT,
    temps_estime VARCHAR(255),
    nb_place INT,
    lieu_depart_id INT NOT NULL,
    lieu_arrivee_id INT NOT NULL,
    personne_id INT NOT NULL,
    immatriculation VARCHAR(50) NOT NULL,
    PRIMARY KEY(id_trajet),
    CONSTRAINT trajet_lieu_depart
        FOREIGN KEY(lieu_depart_id) REFERENCES lieu(id_lieu),
    CONSTRAINT trajet_lieu_arrivee
        FOREIGN KEY(lieu_arrivee_id) REFERENCES lieu(id_lieu),
    CONSTRAINT trajet_personne
        FOREIGN KEY(personne_id) REFERENCES personne(id_personne),
    CONSTRAINT trajet_voiture
        FOREIGN KEY(immatriculation) REFERENCES voiture(immatriculation)
);

CREATE TABLE est_passager(
    id_est_passager INT AUTO_INCREMENT,
    personne_id INT,
    trajet_id INT,
    PRIMARY KEY(id_est_passager),
    CONSTRAINT passager_personne
        FOREIGN KEY(personne_id) REFERENCES personne(id_personne),
    CONSTRAINT passager_trajet
        FOREIGN KEY(trajet_id) REFERENCES trajet(id_trajet)
                         ON DELETE CASCADE
);

CREATE TABLE note(
    id_note INT AUTO_INCREMENT,
    personne_id INT,
    trajet_id INT,
    note_obtenue DECIMAL(2,1),
    PRIMARY KEY(id_note),
    CONSTRAINT note_personne
        FOREIGN KEY(personne_id) REFERENCES personne(id_personne),
    CONSTRAINT note_trajet
        FOREIGN KEY(trajet_id) REFERENCES trajet(id_trajet)
                 ON DELETE CASCADE
);


-- Table sexe
INSERT INTO sexe (nom_sexe) VALUES
    ('M'),
    ('F');

-- Table marque
INSERT INTO marque (nom_marque) VALUES
    ('Peugeot'),
    ('Renault'),
    ('Tesla'),
    ('Citroën'),
    ('Toyota');

-- Table type_voiture
INSERT INTO type_voiture (nom_type_voiture) VALUES
    ('Citadine'),
    ('Compacte'),
    ('SUV'),
    ('Berline');

-- Table ville (fictives dans un rayon de 20 km autour de la ville imaginaire "Montelieu")
INSERT INTO ville (code_postal, nom_ville) VALUES
    ('10000', 'Montelieu'),
    ('10001', 'Saint-Verger'),
    ('10002', 'Bois-Charmant'),
    ('10003', 'Vallon-Vert'),
    ('10004', 'Rocheville');

-- Table Modèle
INSERT INTO modele (nom_modele, marque_id) VALUES
    ('208',     1),
    ('Clio',    2),
    ('Model 3', 3),
    ('C3',      4),
    ('Yaris',   5);

-- Table personne
INSERT INTO personne (nom_personne, prenom, date_naissance, adresse, telephone, mail, sexe_id) VALUES
    ('Dupont',  'Jean',   '1988-05-14', '12 rue des Lilas',       '0601020304', 'jean.dupont@mail.com',   1),
    ('Martin',  'Sophie', '1991-07-09', '5 avenue des Platanes',  '0605060708', 'sophie.martin@mail.com', 2),
    ('Bernard', 'Luc',    '1994-02-18', '3 impasse des Mimosas',  '0611223344', 'luc.bernard@mail.com',   1),
    ('Petit',   'Claire', '1986-12-03', '8 chemin des Vignes',    '0622334455', 'claire.petit@mail.com',  2),
    ('Durand',  'Paul',   '1992-09-26', '10 place du Marché',     '0633445566', 'paul.durand@mail.com',   1),
    ('Moreau',  'Julie',  '1990-03-21', '6 rue du Lac Bleu',      '0644556677', 'julie.moreau@mail.com',  2),
    ('Roux',    'Thomas', '1996-06-10', '22 allée des Peupliers', '0655667788', 'thomas.roux@mail.com',   1),
    ('Lemoine', 'Emma',   '1998-11-17', '9 route des Collines',   '0666778899', 'emma.lemoine@mail.com',  2);

-- Table lieu (fictifs, dans un rayon de 20 km)
INSERT INTO lieu (nom_lieu, adresse, ville_id, altitude, capacite_parking, cout_stationnement, places_PMR) VALUES
    ('Centre-ville Montelieu',     'Place de la Mairie',       1, 210, 50,  1.50, 3),
    ('Zone artisanale du Pommier', 'Rue des Artisans',         1, 205, 120, 0.00, 10),
    ('Gare de Saint-Verger',       'Rue de la Gare',           2, 198, 200, 2.00, 20),
    ('Lac de Saint-Verger',        'Chemin du Port',           2, 190, 80,  0.50, 5),
    ('École de Bois-Charmant',     'Rue des Écoliers',         3, 230, 30,  0.00, 2),
    ('Forêt de Vallon-Vert',       'Chemin des Pins',          4, 260, 15,  0.00, 0),
    ('Place du Marché Rocheville', 'Rue des Commerçants',      5, 220, 60,  1.00, 7),
    ('ZAC des Chênes',             'Avenue des Entrepreneurs', 5, 218, 150, 0.00, 30),
    ('Ferme du Petit-Bois',        'Route du Moulin',          3, 240, 20,  0.00, 2),
    ('Parc des Hirondelles',       'Allée du Vent',            4, 255, 40,  0.00, 2);

-- Table voiture
INSERT INTO voiture
(immatriculation, modele_id, personne_id, type_id, couleur, numero_assurance, cout_assurance,
date_derniere_revision, statut, type_carburant, kilometrage, nombre_places, disponibilite) VALUES
('AA-101-AA', 1, 1, 1, 'Rouge',           'ASS-458799',     450.00, '2024-03-10', 'active',       'essence',    125000, 5, TRUE),
('BB-202-BB', 3, 8, 2, 'Noir',            'AXA-7821-FF',    620.50, '2023-11-25', 'en entretien', 'diesel',     98000,  5, FALSE),
('CC-303-CC', 2, 2, 1, 'Bleu nuit',       'POL-2024-XX-555',310.20, '2022-12-01', 'active',       'électrique', 45000,  4, TRUE),
('DD-404-DD', 5, 5, 3, 'Gris métal',      'ASS-997722',     890.00, '2024-01-18', 'hors service', 'diesel',     220000, 5, FALSE),
('EE-505-EE', 4, 3, 1, 'Blanc',           'POL-55-2023-ZZ', 1120.99,'2024-04-02', 'en pause',     'hybride',    35000,  5, TRUE),
('FF-606-FF', 2, 7, 3, 'Bleu clair',      'ASS-XX-777',     200.00, '2021-09-15', 'active',       'électrique', 15000,  2, TRUE),
('GG-707-GG', 3, 4, 1, 'Rouge foncé',     'AXA-TOP-333',    950.80, '2024-02-10', 'en entretien', 'diesel',     185000, 7, FALSE),
('HH-808-HH', 5, 2, 2, 'Jaune',           'ZZZ-1111',       420.00, '2023-05-28', 'active',       'essence',    78000,  5, TRUE),
('AB-111-AB', 1, 8, 3, 'Gris clair',      'POLICE-789-ASS', 999.99, '2022-01-22', 'hors service', 'hybride',    210000, 5, FALSE),
('BC-212-BC', 2, 5, 1, 'Bordeaux',        'MAIF-2222',      520.00, '2023-07-19', 'active',       'diesel',     143000, 5, TRUE),
('CD-313-CD', 4, 3, 3, 'Bleu turquoise',  'ASS-MULTI-555',  300.00, '2024-02-11', 'active',       'essence',    54000,  4, TRUE),
('DE-414-DE', 5, 3, 2, 'Noir brillant',   'AXA-4499-K',     780.10, '2023-10-04', 'en entretien', 'hybride',    92000,  5, FALSE),
('EF-515-EF', 3, 7, 1, 'Orange',          'POL-45-TEST',    260.50, '2021-03-30', 'active',       'essence',    305000, 5, TRUE),
('FG-616-FG', 1, 4, 2, 'Blanc perlé',     'AA-2024-ASSUR',  1350.75,'2024-04-09', 'active',       'électrique', 21000,  4, TRUE),
('GH-717-GH', 2, 2, 3, 'Gris anthracite', 'MACIF-88-77',    480.00, '2023-12-12', 'en pause',     'diesel',     128500, 5, FALSE),
('HI-818-HI', 4, 1, 1, 'Vert olive',      'ASS-OLD-900',    180.00, '2020-09-02', 'hors service', 'essence',    265000, 4, FALSE);


-- table trajet
INSERT INTO trajet (date_trajet, heure_depart, distance, temps_estime, nb_place, lieu_depart_id, lieu_arrivee_id, personne_id, immatriculation) VALUES
    ('2025-11-30', '07:15:00', 5,  '7 min',  3, 1, 3, 1, 'AA-101-AA'),
    ('2025-09-14', '08:45:00', 6,  '9 min',  2, 2, 4, 2, 'BB-202-BB'),
    ('2025-10-11', '12:30:00', 7,  '10 min', 3, 3, 5, 3, 'CC-303-CC'),
    ('2025-11-13', '17:00:00', 8,  '11 min', 4, 4, 6, 4, 'DD-404-DD'),
    ('2025-12-14', '06:50:00', 6,  '8 min',  3, 5, 1, 5, 'EE-505-EE'),
    ('2025-12-05', '09:15:00', 9,  '12 min', 3, 6, 2, 6, 'FF-606-FF'),
    ('2025-11-25', '13:20:00', 7,  '9 min',  2, 7, 3, 7, 'GG-707-GG'),
    ('2025-11-15', '18:05:00', 10, '14 min', 3, 8, 4, 8, 'HH-808-HH'),
    ('2026-01-16', '07:10:00', 5,  '7 min',  3, 1, 5, 1, 'AB-111-AB'),
    ('2026-01-06', '08:30:00', 8,  '10 min', 2, 2, 6, 2, 'BC-212-BC'),
    ('2026-01-16', '09:45:00', 6,  '8 min',  3, 3, 7, 3, 'CD-313-CD'),
    ('2025-12-16', '11:20:00', 7,  '9 min',  4, 4, 8, 4, 'DE-414-DE'),
    ('2025-11-16', '15:50:00', 9,  '12 min', 3, 5, 1, 5, 'EF-515-EF'),
    ('2025-11-17', '07:25:00', 6,  '8 min',  3, 6, 2, 6, 'FG-616-FG'),
    ('2026-01-03', '08:55:00', 5,  '7 min',  2, 7, 3, 7, 'GH-717-GH'),
    ('2026-01-07', '09:40:00', 7,  '9 min',  3, 8, 4, 8, 'HI-818-HI'),
    ('2026-01-17', '12:10:00', 8,  '10 min', 3, 1, 5, 1, 'AA-101-AA'),
    ('2025-11-17', '14:35:00', 9,  '11 min', 2, 2, 6, 2, 'BB-202-BB'),
    ('2025-12-24', '07:05:00', 6,  '8 min',  3, 3, 7, 3, 'CC-303-CC'),
    ('2025-12-23', '08:20:00', 7,  '9 min',  2, 4, 8, 4, 'DD-404-DD'),
    ('2026-01-18', '09:50:00', 5,  '7 min',  3, 5, 1, 5, 'EE-505-EE'),
    ('2025-12-18', '12:10:00', 8,  '10 min', 4, 6, 2, 6, 'FF-606-FF'),
    ('2025-11-18', '14:35:00', 9,  '11 min', 3, 7, 3, 7, 'GG-707-GG'),
    ('2025-12-27', '16:20:00', 7,  '9 min',  3, 8, 4, 8, 'HH-808-HH'),
    ('2025-11-20', '07:30:00', 6,  '8 min',  3, 1, 5, 1, 'AA-101-AA'),
    ('2025-11-22', '08:45:00', 8,  '10 min', 2, 2, 6, 2, 'BB-202-BB'),
    ('2026-01-19', '09:30:00', 5,  '7 min',  3, 3, 7, 3, 'CC-303-CC'),
    ('2025-11-19', '11:00:00', 7,  '9 min',  4, 4, 8, 4, 'DD-404-DD'),
    ('2025-12-19', '13:25:00', 9,  '12 min', 3, 5, 1, 5, 'EE-505-EE');


-- Table est_passager
INSERT INTO est_passager (personne_id, trajet_id) VALUES
    (2, 1), (3, 1),
    (1, 2), (4, 2),
    (2, 3),
    (5, 4), (6, 4),
    (7, 5),
    (8, 6), (1, 6),
    (3, 7), (5, 7),
    (6, 8), (2, 8);

-- Table note
INSERT INTO note (personne_id, trajet_id, note_obtenue) VALUES
    (2, 1, 4.8), (3, 1, 5.0),
    (1, 2, 4.7), (4, 2, 4.5),
    (2, 3, 4.9),
    (5, 4, 4.6), (6, 4, 4.7),
    (7, 5, 4.8),
    (8, 6, 4.9), (1, 6, 5.0),
    (3, 7, 4.7), (5, 7, 4.9),
    (6, 8, 4.5), (2, 8, 4.8);
