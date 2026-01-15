from flask import Flask, request, render_template, redirect, flash
from pymysql.protocol import NULL_COLUMN

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = 'une cle(token) : grain de sel(any random string)'

## à ajouter
from flask import session, g
import pymysql.cursors

def get_db():
    if 'db' not in g:
        g.db =  pymysql.connect(
            host="", #mettre l'hôte utilisée (localhost ou un serveur externe)
            user="", #entrer le nom de l'utilisateur SQL
            password="",#entrer le mot de passe de cet utilisateur
            database="", #entrer le nom de la base de donnée
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        activate_db_options(g.db)
    return g.db

@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def activate_db_options(db):
    cursor = db.cursor()
    # Vérifier et activer l'option ONLY_FULL_GROUP_BY si nécessaire
    cursor.execute("SHOW VARIABLES LIKE 'sql_mode'")
    result = cursor.fetchone()
    if result:
        modes = result['Value'].split(',')
        if 'ONLY_FULL_GROUP_BY' not in modes:
            print('MYSQL : il manque le mode ONLY_FULL_GROUP_BY')   # mettre en commentaire
            cursor.execute("SET sql_mode=(SELECT CONCAT(@@sql_mode, ',ONLY_FULL_GROUP_BY'))")
            db.commit()
        else:
            print('MYSQL : mode ONLY_FULL_GROUP_BY  ok')   # mettre en commentaire
    # Vérifier et activer l'option lower_case_table_names si nécessaire
    cursor.execute("SHOW VARIABLES LIKE 'lower_case_table_names'")
    result = cursor.fetchone()
    if result:
        if result['Value'] != '0':
            print('MYSQL : valeur de la variable globale lower_case_table_names differente de 0')   # mettre en commentaire
            cursor.execute("SET GLOBAL lower_case_table_names = 0")
            db.commit()
        else :
            print('MYSQL : variable globale lower_case_table_names=0  ok')    # mettre en commentaire
    cursor.close()


@app.route('/', methods=['GET'])
def show_layout():
    return render_template('layout.html')

@app.route('/trajets/show', methods=['GET'])
def show_trajets():
    mycursor = get_db().cursor()
    sql='''SELECT CONCAT(personne.nom_personne, ' ', personne.prenom) as conducteur,
                  trajet.id_trajet as id,
                  trajet.date_trajet as date,
                  trajet.distance as distance,
                  trajet.temps_estime as temps_estime,
                  trajet.nb_place as nb_places,
                  trajet.heure_Depart as heure,
                  voiture.immatriculation as immatriculation,
                  marque.nom_marque as marque,
                  modele.nom_modele as modele,
                  l1.nom_lieu as depart,
                  l2.nom_lieu as destination
           FROM trajet
               INNER JOIN personne ON trajet.personne_id = personne.id_personne
               INNER JOIN lieu l1 ON trajet.lieu_depart_id = l1.id_lieu
               INNER JOIN lieu l2 ON trajet.lieu_arrivee_id = l2.id_lieu
               INNER JOIN voiture ON trajet.immatriculation = voiture.immatriculation
               INNER JOIN modele ON voiture.modele_id = modele.id_modele
               INNER JOIN marque ON modele.marque_id = marque.id_marque
           ORDER BY trajet.id_trajet;'''

    mycursor.execute(sql)
    trajets = mycursor.fetchall()

    mycursor = get_db().cursor()
    sql='''SELECT CONCAT(lieu.nom_lieu, ', ', lieu.adresse, ', ', ville.code_postal, ' ', ville.nom_ville) as adresse,
                  lieu.id_lieu as id
           FROM lieu
                    INNER JOIN ville ON lieu.ville_id = ville.id_ville;'''

    mycursor.execute(sql)
    lieux = mycursor.fetchall()

    return render_template('trajets/show_trajets.html', trajets=trajets, lieux=lieux)

@app.route('/trajets/search', methods=['POST'])
def search_trajet():
    date = request.form.get('date','')
    depart = request.form.get('depart','')
    arrivee = request.form.get('arrivee','')
    nb_place = request.form.get('nb_place','')

    where=""
    if date != '':
        where+= f"(CONCAT(date_trajet,' ',heure_depart) BETWEEN NOW() AND \"{date}\")"

    if depart != '':
        if where != '':
            where += ' AND '
        where += f"lieu_depart_id = {int(depart)}"

    if arrivee != '':
        if where != '':
            where += ' AND '
        where += f"lieu_arrivee_id = {int(arrivee)}"

    if nb_place != '':
        if where != '':
            where += ' AND '
        where += f"nb_place >= {int(nb_place)}"

    print(where)
    mycursor = get_db().cursor()
    if where=='':
        sql = '''SELECT CONCAT(personne.nom_personne, ' ', personne.prenom) as conducteur, \
                        trajet.id_trajet                                    as id,
                        trajet.date_trajet as date,
                        trajet.distance as distance,
                        trajet.temps_estime as temps_estime,
                        trajet.nb_place as nb_places,
                        trajet.heure_Depart as heure,
                        voiture.immatriculation as immatriculation,
                        marque.nom_marque as marque,
                        modele.nom_modele as modele,
                        l1.nom_lieu as depart,
                        l2.nom_lieu as destination
                 FROM trajet
                     INNER JOIN personne \
                 ON trajet.personne_id = personne.id_personne
                     INNER JOIN lieu l1 ON trajet.lieu_depart_id = l1.id_lieu
                     INNER JOIN lieu l2 ON trajet.lieu_arrivee_id = l2.id_lieu
                     INNER JOIN voiture ON trajet.immatriculation = voiture.immatriculation
                     INNER JOIN modele ON voiture.modele_id = modele.id_modele
                     INNER JOIN marque ON modele.marque_id = marque.id_marque
                 ORDER BY trajet.id_trajet;'''
        mycursor.execute(sql)

    else:
        sql = f'''SELECT CONCAT(personne.nom_personne, ' ', personne.prenom) as conducteur, \
                        trajet.id_trajet                                    as id,
                        trajet.date_trajet as date,
                        trajet.distance as distance,
                        trajet.temps_estime as temps_estime,
                        trajet.nb_place as nb_places,
                        trajet.heure_Depart as heure,
                        voiture.immatriculation as immatriculation,
                        marque.nom_marque as marque,
                        modele.nom_modele as modele,
                        l1.nom_lieu as depart,
                        l2.nom_lieu as destination
                 FROM trajet
                     INNER JOIN personne \
                 ON trajet.personne_id = personne.id_personne
                     INNER JOIN lieu l1 ON trajet.lieu_depart_id = l1.id_lieu
                     INNER JOIN lieu l2 ON trajet.lieu_arrivee_id = l2.id_lieu
                     INNER JOIN voiture ON trajet.immatriculation = voiture.immatriculation
                     INNER JOIN modele ON voiture.modele_id = modele.id_modele
                     INNER JOIN marque ON modele.marque_id = marque.id_marque
                 WHERE {where}
                 ORDER BY trajet.id_trajet;'''
        mycursor.execute(sql)

    trajets = mycursor.fetchall()

    mycursor = get_db().cursor()
    sql='''SELECT CONCAT(lieu.nom_lieu, ', ', lieu.adresse, ', ', ville.code_postal, ' ', ville.nom_ville) as adresse,
                  lieu.id_lieu as id
           FROM lieu
                    INNER JOIN ville ON lieu.ville_id = ville.id_ville
           WHERE nom_lieu!='None';'''

    mycursor.execute(sql)
    lieux = mycursor.fetchall()

    message = f"Trajets filtrés : --nombre_places : {nb_place} --lieu_depart  : {depart} --lieu_arrivee : {arrivee} --date : entre aujourd'hui et {date}"
    flash(message, 'alert-success')

    return render_template('trajets/show_trajets.html', trajets=trajets, lieux=lieux)


@app.route('/trajets/edit', methods=['GET'])
def edit_trajet():
    id = request.args.get('id')
    mycursor = get_db().cursor()
    sql='''SELECT CONCAT(personne.nom_personne, ' ', personne.prenom) as conducteur,
                  trajet.personne_id,
                  trajet.id_trajet as id,
                  trajet.date_trajet as date,
                  trajet.distance as distance,
                  trajet.temps_estime as temps_estime,
                  trajet.nb_place as nb_places,
                  trajet.heure_Depart as heure,
                  voiture.immatriculation as immatriculation,
                  trajet.lieu_depart_id as depart,
                  trajet.lieu_arrivee_id as destination
           FROM trajet
               INNER JOIN personne ON trajet.personne_id = personne.id_personne
               INNER JOIN voiture ON trajet.immatriculation = voiture.immatriculation
           WHERE id_trajet = %s;'''
    mycursor.execute(sql, id)
    trajet = mycursor.fetchone()

    mycursor = get_db().cursor()
    sql = '''SELECT CONCAT(personne.nom_personne, ' ', personne.prenom) as conducteur, \
                    personne.id_personne as id
             FROM personne;'''
    mycursor.execute(sql)
    conducteurs = mycursor.fetchall()

    mycursor = get_db().cursor()
    sql = '''SELECT CONCAT(voiture.immatriculation, ' ', type_voiture.nom_type_voiture, ' ', modele.nom_modele, ' ', marque.nom_marque) as voiture, \
                    voiture.immatriculation
             FROM voiture
                      INNER JOIN modele ON voiture.modele_id = modele.id_modele
                      INNER JOIN type_voiture ON voiture.type_id = type_voiture.id_type
                      INNER JOIN marque ON modele.marque_id = marque.id_marque;
          '''
    mycursor.execute(sql)
    voitures = mycursor.fetchall()

    mycursor = get_db().cursor()
    sql='''SELECT CONCAT(lieu.nom_lieu, ', ', lieu.adresse, ', ', ville.code_postal, ' ', ville.nom_ville) as adresse,
                  lieu.id_lieu as id
           FROM lieu
                    INNER JOIN ville ON lieu.ville_id = ville.id_ville
           WHERE nom_lieu != "None";'''
    mycursor.execute(sql)
    lieux = mycursor.fetchall()

    return render_template('/trajets/edit_trajets.html', trajet=trajet, conducteurs=conducteurs, voitures=voitures, lieux=lieux)

@app.route('/trajets/edit', methods=['POST'])
def valid_edit_trajet():
    id_trajet = request.form.get('id','')
    date = request.form.get('date', '')
    id_conducteur = request.form.get('conducteur', '')
    distance = request.form.get('distance', '')
    temps_estime = request.form.get('temps_estime', '')
    nb_places = request.form.get('nb_places', '')
    heure = request.form.get('heure', '')
    immatriculation = request.form.get('voiture', '')
    id_depart = request.form.get('depart', '')
    id_arrivee = request.form.get('arrivee', '')

    tuple_param = (date, id_conducteur, distance, temps_estime, nb_places, heure, immatriculation, id_depart, id_arrivee, id_trajet)
    mycursor = get_db().cursor()
    sql='''UPDATE trajet
           SET date_trajet=%s,
               personne_id=%s,
               distance=%s,
               temps_estime=%s,
               nb_place=%s,
               heure_depart=%s,
               immatriculation=%s,
               lieu_depart_id=%s,
               lieu_arrivee_id=%s
           WHERE id_trajet=%s'''


    mycursor.execute(sql, tuple_param)
    get_db().commit()

    message = f"trajet modifie : --date : {date} --conducteur : {id_conducteur} --distance : {distance} --temps_estime : {temps_estime} --nb_places : {nb_places} --heure_depart : {heure} --immatriculation : {immatriculation} --lieu_depart : {id_depart} --lieu_arrive : {id_arrivee} --pour le trajet d'id : {id_trajet}"
    flash(message, 'alert-success')

    return redirect('/trajets/show')

@app.route('/trajets/delete', methods=['GET'])
def delete_trajet():
    id = request.args.get('id')
    mycursor = get_db().cursor()
    sql='''DELETE FROM trajet
           WHERE id_trajet = %s;'''
    mycursor.execute(sql, id)
    get_db().commit()

    message = f"attention : trajet supprimé id = {id}"
    flash(message, 'alert-warning')
    return redirect('/trajets/show')


@app.route('/trajets/add', methods=['GET'])
def add_trajet():
    mycursor = get_db().cursor()
    sql = '''SELECT CONCAT(personne.nom_personne, ' ', personne.prenom) as conducteur, \
                    personne.id_personne as id
             FROM personne;'''
    mycursor.execute(sql)
    conducteurs = mycursor.fetchall()

    mycursor = get_db().cursor()
    sql = '''SELECT CONCAT(voiture.immatriculation, ' ', type_voiture.nom_type_voiture, ' ', modele.nom_modele, ' ', marque.nom_marque) as voiture, \
                    voiture.immatriculation
             FROM voiture
                      INNER JOIN modele ON voiture.modele_id = modele.id_modele
                      INNER JOIN type_voiture ON voiture.type_id = type_voiture.id_type
                      INNER JOIN marque ON modele.marque_id = marque.id_marque;
          '''
    mycursor.execute(sql)
    voitures = mycursor.fetchall()

    mycursor = get_db().cursor()
    sql='''SELECT CONCAT(lieu.nom_lieu, ', ', lieu.adresse, ', ', ville.code_postal, ' ', ville.nom_ville) as adresse,
                  lieu.id_lieu as id
           FROM lieu
                    INNER JOIN ville ON lieu.ville_id = ville.id_ville
           WHERE nom_lieu!="None";'''
    mycursor.execute(sql)
    lieux = mycursor.fetchall()

    return render_template('/trajets/add_trajets.html', conducteurs=conducteurs, voitures=voitures, lieux=lieux)


@app.route('/trajets/add', methods=['POST'])
def valid_add_trajet():
    date = request.form.get('date', '')
    id_conducteur = request.form.get('conducteur', '')
    distance = request.form.get('distance', '')
    temps_estime = request.form.get('temps_estime', '')
    nb_places = request.form.get('nb_places', '')
    heure = request.form.get('heure', '')
    immatriculation = request.form.get('voiture', '')
    id_depart = request.form.get('depart', '')
    id_arrivee = request.form.get('arrivee', '')

    tuple_param = [date, id_conducteur, distance, temps_estime, nb_places, heure, immatriculation, id_depart, id_arrivee]

    for i in range(len(tuple_param)):
        if tuple_param[i] == '':
            tuple_param[i] = None
    mycursor = get_db().cursor()
    sql='''INSERT INTO trajet (date_trajet, personne_id, distance, temps_estime, nb_place, heure_depart, immatriculation, lieu_depart_id, lieu_arrivee_id)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);'''


    mycursor.execute(sql, tuple_param)
    get_db().commit()

    message = f"trajet ajouté : --date : {date} --conducteur : {id_conducteur} --distance : {distance} --temps_estime : {temps_estime} --nb_places : {nb_places} --heure_depart : {heure} --immatriculation : {immatriculation} --lieu_depart : {id_depart} --lieu_arrive : {id_arrivee}"
    flash(message, 'alert-success')

    return redirect('/trajets/show')


@app.route('/trajets/etat', methods=['GET'])
def etat_trajet():
    mycursor = get_db().cursor()
    sql='''SELECT sexe.nom_sexe as sexe,
                  count(*) as nb_trajets
           FROM trajet
                    INNER JOIN personne on trajet.personne_id = personne.id_personne
                    INNER JOIN sexe on personne.sexe_id = sexe.id_sexe
           GROUP BY sexe.nom_sexe;'''
    mycursor.execute(sql)
    trajets_sexe = mycursor.fetchall()

    sql='''SELECT ROUND(AVG(note.note_obtenue), 2) as note_conducteur,
                  CONCAT(personne.nom_personne, ' ', personne.prenom) as Conducteur,
                  count(*) as nb_trajets
           FROM trajet
                    INNER JOIN note on trajet.id_trajet = note.trajet_id
                    INNER JOIN personne on trajet.personne_id = personne.id_personne
           GROUP BY Conducteur;'''

    mycursor.execute(sql)
    trajets_note = mycursor.fetchall()

    sql='''SELECT CONCAT(personne.nom_personne, ' ', personne.prenom) as conducteur,
                  SUM(trajet.distance) as total_distance_conduite,
                  count(*) as nb_trajets,
                  ROUND(AVG(trajet.distance), 2) as distance_moyenne
           FROM trajet
                    INNER JOIN personne ON trajet.personne_id = personne.id_personne
           WHERE trajet.date_trajet < CURRENT_DATE()
           GROUP BY conducteur;'''
    mycursor.execute(sql)
    trajets_distance = mycursor.fetchall()

    return render_template('/trajets/etat_trajets.html', trajets_sexe=trajets_sexe, trajets_note=trajets_note, trajets_distance=trajets_distance)


@app.route('/lieu/show', methods=['GET'])
def show_lieu():
    mycursor = get_db().cursor()
    sql = ''' SELECT lieu.id_lieu as id,
                     lieu.nom_lieu as nom,
                     lieu.adresse as adresse,
                     lieu.altitude as altitude,
                     lieu.capacite_parking as capaciteParking,
                     lieu.cout_stationnement as cout_stationnement,
                     lieu.places_PMR as place_PMR,
                     ville.nom_ville as ville
              FROM lieu
                       INNER JOIN ville ON lieu.ville_id = ville.id_ville
              ORDER BY lieu.id_lieu;'''

    mycursor.execute(sql)
    lieux = mycursor.fetchall()
    return render_template('lieu/show_lieu.html', lieux=lieux)

@app.route('/lieu/edit', methods=['GET'])
def edit_lieu():
    id = request.args.get('id')
    mycursor = get_db().cursor()
    sql = ''' SELECT lieu.id_lieu            as id,
                     lieu.nom_lieu           as nom,
                     lieu.adresse            as adresse,
                     lieu.altitude           as altitude,
                     lieu.capacite_parking   as capacite_parking,
                     lieu.cout_stationnement as cout_stationnement,
                     lieu.places_PMR         as place_PMR,
                     ville.nom_ville as ville
              FROM lieu
                       INNER JOIN ville ON lieu.ville_id = ville.id_ville
              WHERE id_lieu = %s;'''
    mycursor.execute(sql, id)
    lieu = mycursor.fetchone()


    mycursor = get_db().cursor()
    sql = '''SELECT ville.nom_ville as ville, \
                    ville.id_ville as id
             FROM ville;'''
    mycursor.execute(sql)
    villes = mycursor.fetchall()

    return render_template('/lieu/edit_lieu.html', lieu=lieu, villes=villes)

@app.route('/lieu/edit', methods=['POST'])
def valid_edit_lieu():
    id_lieu = int(request.form.get('id',''))
    nom = request.form.get('nom', '')
    ville = int(request.form.get('ville', ''))
    adresse = request.form.get('adresse', '')
    altitude = int(request.form.get('altitude', ''))
    capacite_parking = int(request.form.get('capacite_parking', ''))
    cout_stationnement = float(request.form.get('cout_stationnement', ''))
    places_PMR = int(request.form.get('places_PMR', ''))

    tuple_param = (nom, ville, adresse, altitude, capacite_parking, cout_stationnement, places_PMR, id_lieu)
    mycursor = get_db().cursor()
    sql='''UPDATE lieu
           SET nom_lieu=%s,
               ville_id=%s,
               adresse=%s,
               altitude=%s,
               capacite_parking=%s,
               cout_stationnement=%s,
               places_PMR=%s
           WHERE id_lieu=%s'''

    mycursor.execute(sql, tuple_param)
    get_db().commit()


    message = f'lieu modifié, nom: {nom} ---- ville_id: {ville} ---- adresse: {adresse} - altitude: {altitude} - capacite_parking: {capacite_parking} - cout_stationnement: {cout_stationnement} - places_PMR: {places_PMR} pour le lieu d\'identifiant: {id_lieu}'
    print(message)
    flash(message, 'alert-success')
    return redirect('/lieu/show')

@app.route('/lieu/add', methods=['GET'])
def add_lieu():
    mycursor = get_db().cursor()
    sql='''SELECT ville.nom_ville as nom,
                  ville.id_ville as id
           FROM ville
           ORDER BY ville.nom_ville;'''
    mycursor.execute(sql)
    villes = mycursor.fetchall()
    print(villes)

    return render_template('/lieu/add_lieu.html',  villes=villes)

@app.route('/lieu/add', methods=['POST'])
def valid_add_lieu():
    nom = request.form.get('nom', None)
    ville = request.form.get('ville', None)
    adresse = request.form.get('adresse', None)
    altitude = request.form.get('altitude', None)
    capacite_parking = request.form.get('capacite_parking', None)
    cout_stationnement = request.form.get('cout_stationnement', None)
    places_PMR = request.form.get('places_PMR', None)

    tuple_param = [nom, ville, adresse, altitude, capacite_parking, cout_stationnement, places_PMR]

    for i in range(len(tuple_param)):
        if tuple_param[i] == '':
            tuple_param[i] = None
    mycursor = get_db().cursor()
    sql='''INSERT INTO lieu (nom_lieu, ville_id, adresse, altitude, capacite_parking, cout_stationnement, places_PMR)
           VALUES (%s, %s, %s, %s, %s, %s, %s);'''


    mycursor.execute(sql, tuple_param)
    get_db().commit()

    message = f'lieu ajouté, nom: {nom} ---- ville_id: {ville} ---- adresse: {adresse} - altitude: {altitude} - capacite_parking: {capacite_parking} - cout_stationnement: {cout_stationnement} - places_PMR: {places_PMR}'
    print(message)
    flash(message, 'alert-success')
    return redirect('/lieu/show')


@app.route('/lieu/delete', methods=['GET'])
def delete_lieu():
    id = int(request.args.get('id'))
    mycursor = get_db().cursor()
    requete1=f'''DELETE FROM trajet where lieu_depart_id={id} OR lieu_arrivee_id={id};'''
    mycursor.execute(requete1)
    get_db().commit()

    mycursor = get_db().cursor()
    requete2=f'''DELETE FROM lieu where id_lieu={id};'''
    mycursor.execute(requete2)
    get_db().commit()

    flash("Lieu et trajets associés supprimés avec succès", 'alert-success')
    return redirect('/lieu/show')

@app.route('/lieu/etat', methods=['GET'])
def etat_lieu():
    mycursor = get_db().cursor()
    sql = ''' SELECT lieu.id_lieu                               as id,
                     lieu.nom_lieu                              as lieu,
                     COUNT(trajet.id_trajet)                    as trajetAssocie,
                     lieu.capacite_parking                      as capacite,
                     lieu.places_PMR                            as place_PMR,
                     (lieu.capacite_parking - lieu.places_PMR)  as places_non_PMR,
                     AVG(trajet.distance)                       as distance_moyenne,
                     ville.nom_ville                            as ville
              FROM lieu
                       INNER JOIN ville ON lieu.ville_id = ville.id_ville
                       INNER JOIN trajet ON trajet.lieu_arrivee_id = lieu.id_lieu OR trajet.lieu_depart_id = lieu.id_lieu
              GROUP BY lieu.id_lieu
              ORDER BY lieu.nom_lieu;
          '''

    mycursor.execute(sql)
    lieux = mycursor.fetchall()

    mycursor = get_db().cursor()
    sql = ''' SELECT lieu.id_lieu                                      as id,
                     lieu.nom_lieu                                     as nom,
                     lieu.adresse                                      as adresse,
                     lieu.altitude                                     as altitude,
                     lieu.cout_stationnement                           as cout_stationnement,
                     COUNT(trajet.id_trajet)                           as trajetAssocie,
                     lieu.capacite_parking                             as capacite,
                     lieu.places_PMR                                   as place_PMR,
                     (lieu.capacite_parking - lieu.places_PMR)         as places_non_PMR,
                     ville.nom_ville                                   as ville,
                     (lieu.cout_stationnement / lieu.capacite_parking) as rentabilite
              FROM lieu
                       INNER JOIN ville ON lieu.ville_id = ville.id_ville
                       INNER JOIN trajet \
                                  ON trajet.lieu_arrivee_id = lieu.id_lieu OR trajet.lieu_depart_id = lieu.id_lieu
              GROUP BY lieu.id_lieu
              ORDER BY (lieu.cout_stationnement / lieu.capacite_parking) ;'''

    mycursor.execute(sql)
    cout = mycursor.fetchall()

    mycursor = get_db().cursor()
    sql = ''' SELECT COUNT(DISTINCT lieu.id_lieu )                              as nombre_lieu,
                     COUNT(DISTINCT trajet.id_trajet)                           as trajet
              FROM lieu
                       INNER JOIN ville ON lieu.ville_id = ville.id_ville
                       INNER JOIN trajet \
                                  ON trajet.lieu_arrivee_id = lieu.id_lieu OR trajet.lieu_depart_id = lieu.id_lieu
              ORDER BY lieu.nom_lieu;'''

    mycursor.execute(sql)
    total = mycursor.fetchone()
    return render_template('/lieu/etat_lieu.html', lieux=lieux, cout=cout, total=total)



@app.route('/voiture/show', methods=['GET'])
def show_voiture():
    mycursor = get_db().cursor()
    sql = '''SELECT
                 voiture.immatriculation AS id,
                 voiture.couleur AS couleur,
                 voiture.numero_assurance AS numero_assurance,
                 voiture.cout_assurance AS cout_assurance,
                 voiture.date_derniere_revision AS date_derniere_revision,
                 voiture.type_carburant AS type_carburant,
                 voiture.kilometrage AS kilometrage,
                 voiture.nombre_places AS nombre_place,
                 voiture.disponibilite AS disponibilite,
                 voiture.statut AS statut,
                 voiture.modele_id AS modele,
                 voiture.type_id AS type,
                 voiture.personne_id AS personne
             FROM voiture
                      INNER JOIN personne ON voiture.personne_id = personne.id_personne
                      INNER JOIN type_voiture ON voiture.type_id = type_voiture.id_type
                      INNER JOIN modele ON voiture.modele_id = modele.id_modele;'''
    mycursor.execute(sql)
    voitures = mycursor.fetchall()
    return render_template('voiture/show_voiture.html', voitures=voitures)

@app.route('/voiture/edit', methods=['GET'])
def edit_voiture():
    immatriculation = request.args.get('id')
    mycursor = get_db().cursor()
    sql = '''
          SELECT voiture.immatriculation AS id,
                 voiture.couleur,
                 voiture.numero_assurance,
                 voiture.cout_assurance,
                 voiture.date_derniere_revision,
                 voiture.statut,
                 voiture.modele_id,
                 voiture.type_carburant,
                 voiture.kilometrage,
                 voiture.nombre_places,
                 voiture.disponibilite,
                 voiture.type_id
          FROM voiture
          WHERE voiture.immatriculation = %s \
          '''
    mycursor.execute(sql, (immatriculation,))
    voiture = mycursor.fetchone()

    mycursor = get_db().cursor()
    sql = '''SELECT id_modele, nom_modele FROM modele'''
    mycursor.execute(sql)
    modeles = mycursor.fetchall()

    mycursor = get_db().cursor()
    sql = '''SELECT id_type, nom_type_voiture FROM type_voiture'''
    mycursor.execute(sql)
    types = mycursor.fetchall()

    mycursor = get_db().cursor()
    sql = '''SELECT id_personne, CONCAT(nom_personne,' ', prenom) as nom_personne FROM personne'''
    mycursor.execute(sql)
    personnes = mycursor.fetchall()

    statut = ['active', 'en entretien', 'hors service', 'en pause']
    carburant = ['essence', 'diesel', 'électrique', 'hybride']
    disponibilite = ['Disponible', 'Indisponible']

    return render_template(
        'voiture/edit_voiture.html',
        voiture=voiture,
        modeles=modeles,
        types=types,
        statut=statut,
        carburant=carburant,
        disponibilite=disponibilite,
        personnes=personnes
    )

@app.route('/voiture/edit', methods=['POST'])
def valid_edit_voiture():
    immatriculation = request.form.get('id')
    couleur = request.form.get('couleur')
    numero_assurance = request.form.get('numero_assurance')
    cout_assurance = request.form.get('cout_assurance')
    date_revision = request.form.get('date_derniere_revision')
    statut = request.form.get('statut')
    modele = request.form.get('modele')
    type_carburant = request.form.get('type_carburant')
    kilometrage = request.form.get('kilometrage')
    nombre_places = request.form.get('nombre_places')
    disponibilite = request.form.get('disponibilite')
    type_id = request.form.get('type_id')
    personne_id = request.form.get('personne_id')

    sql = '''
          UPDATE voiture SET
                             couleur=%s,
                             numero_assurance=%s,
                             cout_assurance=%s,
                             date_derniere_revision=%s,
                             statut=%s,
                             modele_id=%s,
                             type_carburant=%s,
                             kilometrage=%s,
                             nombre_places=%s,
                             disponibilite=%s,
                             type_id=%s,
                             personne_id = %s
          WHERE immatriculation=%s \
          '''

    params = (couleur, numero_assurance, cout_assurance, date_revision, statut,
              modele, type_carburant, kilometrage, nombre_places, disponibilite,
              type_id, personne_id, immatriculation)

    mycursor = get_db().cursor()
    mycursor.execute(sql, params)
    get_db().commit()

    message = f"voiture modifiée : --immatriculation : {immatriculation} --couleur : {couleur} --num_assurance : {numero_assurance} --cout_assurance : {cout_assurance} --date_revision : {date_revision} --statut : {statut} --modele : {modele} --type_carburant : {type_carburant} --kilometrage : {kilometrage} --nombre_places : {nombre_places} --disponibilite : {disponibilite} --type_id : {type_id} --proprietaire : {personne_id}"
    flash(message, 'alert-success')

    return redirect('/voiture/show')

@app.route('/voiture/delete', methods=['GET'])
def delete_voiture():
    id = request.args.get('id')
    mycursor = get_db().cursor()
    requete1 = '''DELETE \
                  FROM trajet \
                  WHERE immatriculation = %s'''
    mycursor.execute(requete1, (id,))
    get_db().commit()

    mycursor = get_db().cursor()
    requete2 = '''DELETE \
                  FROM voiture \
                  WHERE immatriculation = %s'''
    mycursor.execute(requete2, (id,))
    get_db().commit()

    flash("Voiture et trajets associés supprimés avec succès", 'alert-success')
    return redirect('/voiture/show')

@app.route('/voiture/add', methods=['GET'])
def add_voiture():
    mycursor = get_db().cursor()
    sql='''SELECT modele.nom_modele as nom_modele,
                  modele.id_modele as id_modele
           FROM modele
           ORDER BY modele.nom_modele;'''
    mycursor.execute(sql)
    modeles = mycursor.fetchall()

    mycursor = get_db().cursor()
    sql = '''SELECT personne.nom_personne as nom_personne, \
                    personne.id_personne as id_personne
           FROM personne
           ORDER BY personne.nom_personne;'''
    mycursor.execute(sql)
    personnes = mycursor.fetchall()

    mycursor = get_db().cursor()
    sql = '''SELECT type_voiture.nom_type_voiture as nom_type_voiture, \
                    type_voiture.id_type  as id_type
             FROM type_voiture
             ORDER BY type_voiture.nom_type_voiture;'''
    mycursor.execute(sql)
    types = mycursor.fetchall()

    statut = ['active', 'en entretien', 'hors service', 'en pause']
    carburant = ['essence', 'diesel', 'électrique', 'hybride']
    disponibilite = ['Disponible', 'Indisponible']


    return render_template('/voiture/add_voiture.html',  modeles=modeles, personnes=personnes, types=types, statut=statut, carburant=carburant, disponibilite=disponibilite)

@app.route('/voiture/add', methods=['POST'])
def valid_add_voiture():
    immatriculation = request.form.get('id')
    couleur = request.form.get('couleur')
    numero_assurance = request.form.get('numero_assurance')
    cout_assurance = request.form.get('cout_assurance')
    date_revision = request.form.get('date_derniere_revision')
    statut = request.form.get('statut')
    modele = request.form.get('modele')
    type_carburant = request.form.get('type_carburant')
    kilometrage = request.form.get('kilometrage')
    nombre_places = request.form.get('nombre_places')
    disponibilite = request.form.get('disponibilite')
    type_id = request.form.get('type_id')
    personne_id = request.form.get('personne_id')

    mycursor = get_db().cursor()
    sql='''INSERT INTO voiture(immatriculation, couleur, numero_assurance, cout_assurance, date_derniere_revision, statut, type_carburant, modele_id, kilometrage, nombre_places, disponibilite, type_id, personne_id)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'''

    tuple_param = (immatriculation, couleur, numero_assurance, cout_assurance, date_revision, statut, modele, type_carburant, kilometrage, nombre_places, disponibilite, type_id, personne_id)
    mycursor.execute(sql, tuple_param)
    get_db().commit()

    message = f"voiture modifiée : --immatriculation : {immatriculation} --couleur : {couleur} --num_assurance : {numero_assurance} --cout_assurance : {cout_assurance} --date_revision : {date_revision} --statut : {statut} --modele : {modele} --type_carburant : {type_carburant} --kilometrage : {kilometrage} --nombre_places : {nombre_places} --disponibilite : {disponibilite} --type_id : {type_id} --personne_id : {personne_id}"
    flash(message, 'alert-success')
    return redirect('/voiture/show')




if __name__ == '__main__':
    app.run()
