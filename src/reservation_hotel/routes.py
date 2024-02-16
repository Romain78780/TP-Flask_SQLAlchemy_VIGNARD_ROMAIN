from .database import db
from .models import  Chambre, Reservation
from flask import Flask, request, jsonify, Blueprint
main = Blueprint('main', __name__)
from datetime import datetime
from sqlalchemy import and_, or_

@main.route('/api/chambres', methods=['POST'])
def ajouter_chambre():
    try:
        # Extraction des données de la requête
        data = request.get_json()
        numero = data['numero']
        type_chambre = data['type']
        prix = data['prix']

        # Vérification de l'unicité du numéro de chambre
        if Chambre.query.filter_by(numero=numero).first():
            return jsonify({"success": False, "message": "Une chambre avec ce numéro existe déjà."}), 400

        # Création de la nouvelle chambre
        nouvelle_chambre = Chambre(numero=numero, type=type_chambre, prix=prix)

        # Ajout de la chambre à la base de données
        db.session.add(nouvelle_chambre)
        db.session.commit()

        # Réponse de succès
        return jsonify({"success": True, "message": "Chambre ajoutée avec succès."}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Erreur lors de l'ajout de la chambre: " + str(e)}), 500

@main.route('/api/chambres/<int:id>', methods=['PUT'])
def modifier_chambre(id):
    # Récupération de la chambre par son ID
    chambre = Chambre.query.get(id)
    
    if not chambre:
        return jsonify({"success": False, "message": "Chambre non trouvée."}), 404

    data = request.get_json()
    
    # Mise à jour des attributs de la chambre avec les nouvelles valeurs
    chambre.numero = data.get('numero', chambre.numero)
    chambre.type = data.get('type', chambre.type)
    chambre.prix = data.get('prix', chambre.prix)
    
    # Enregistrement des modifications dans la base de données
    db.session.commit()
    
    return jsonify({"success": True, "message": "Chambre mise à jour avec succès."})   

@main.route('/api/chambres/<int:id>', methods=['DELETE'])
def supprimer_chambre(id):
    # Récupération de la chambre par son ID
    chambre = Chambre.query.get(id)
    
    if not chambre:
        return jsonify({"success": False, "message": "Chambre non trouvée."}), 404
    
    # Suppression de la chambre
    db.session.delete(chambre)
    
    # Enregistrement de la suppression dans la base de données
    db.session.commit()
    
    return jsonify({"success": True, "message": "Chambre supprimée avec succès."})

@main.route('/api/reservations', methods=['POST'])
def creer_reservation():
    data = request.get_json()
    
    id_client = data['id_client']
    id_chambre = data['id_chambre']
    date_arrivee = datetime.strptime(data['date_arrivee'], '%Y-%m-%d').date()
    date_depart = datetime.strptime(data['date_depart'], '%Y-%m-%d').date()
    
    # Vérification de la disponibilité de la chambre
    reservations_existantes = Reservation.query.filter(
        Reservation.id_chambre == id_chambre,
        Reservation.date_depart > date_arrivee,
        Reservation.date_arrivee < date_depart
    ).all()
    
    if reservations_existantes:
        return jsonify({"success": False, "message": "La chambre n'est pas disponible pour les dates demandées."}), 400
    
    # Création de la nouvelle réservation
    nouvelle_reservation = Reservation(
        id_client=id_client,
        id_chambre=id_chambre,
        date_arrivee=date_arrivee,
        date_depart=date_depart,
        statut="confirmée"
    )
    db.session.add(nouvelle_reservation)
    db.session.commit()
    
    return jsonify({"success": True, "message": "Réservation créée avec succès."})

@main.route('/api/reservations/<int:id>', methods=['DELETE'])
def annuler_reservation(id):
    # Récupération de la réservation par son ID
    reservation = Reservation.query.get(id)
    
    if not reservation:
        return jsonify({"success": False, "message": "Réservation non trouvée."}), 404
    db.session.delete(reservation)
    
    db.session.commit()
    
    return jsonify({"success": True, "message": "Réservation annulée avec succès."})

@main.route('/api/chambres/disponibles', methods=['GET'])
def rechercher_chambres_disponibles():
    date_arrivee_str = request.args.get('date_arrivee')
    date_depart_str = request.args.get('date_depart')

    # Vérifie si les paramètres 'date_arrivee' et 'date_depart' sont présents et non vides
    if not date_arrivee_str or not date_depart_str:
        return jsonify({"error": "Les paramètres 'date_arrivee' et 'date_depart' sont requis et doivent être non vides."}), 400

    try:
        date_arrivee = datetime.strptime(date_arrivee_str, '%Y-%m-%d').date()
        date_depart = datetime.strptime(date_depart_str, '%Y-%m-%d').date()
    except ValueError:
        # Gère le cas où la conversion de la date échoue
        return jsonify({"error": "Format de date invalide. Utilisez le format 'AAAA-MM-JJ'."}), 400

    # Requête pour trouver les chambres disponibles
    chambres_disponibles = Chambre.query.filter(
        ~Chambre.reservations.any(
            or_(
                Reservation.date_arrivee.between(date_arrivee, date_depart),
                Reservation.date_depart.between(date_arrivee, date_depart),
                and_(
                    Reservation.date_arrivee <= date_arrivee,
                    Reservation.date_depart >= date_depart
                )
            )
        )
    ).all()

    # Formatage des résultats
    resultat = [
        {
            "id": chambre.id,
            "numero": chambre.numero,
            "type": chambre.type,
            "prix": chambre.prix
        } for chambre in chambres_disponibles
    ]

    return jsonify(resultat)