Application de Réservation d'Hôtels


Description

Cette application de réservation d'hôtels permet aux utilisateurs de rechercher des chambres disponibles, de créer des réservations, et d'annuler des réservations existantes.


Routes

Ajouter des chambres : '/api/chambres'
Modifier des chambres : '/api/chambres/<int:id>' --> PUT 
Supprimer des chambres : '/api/chambres/<int:id>' --> DELETE
Recherche de Chambres Disponibles : '/api/chambres/disponibles'
Création de Réservation : '/api/reservations'
Annulation de Réservation : '/api/reservations/<int:id>' --> DELETE



Technologies Utilisées

Flask, SQLAlchemy, SQLite 
