# BloodTrace

Module SIH (Systeme d'Information Hospitalier) de gestion et tracabilite des dons de sang.

## Architecture

BloodTrace est concu comme un module integrable dans un SIH existant, et non comme une application autonome.

### Fonctionnalites principales

- **Gestion des donneurs** : registre des donneurs, eligibilite, historique des dons
- **Inventaire des poches de sang** : suivi par type, composant, statut, date de peremption
- **Demandes de transfusion** : creation, appariement automatique, approbation
- **Tracabilite complete** : chaine donneur -> poche -> patient
- **Compatibilite sanguine** : matrice ABO+Rh complete
- **API FHIR** : endpoints compatibles HL7 FHIR (Patient, Specimen, ServiceRequest)
- **Audit trail** : journalisation de chaque acces et modification
- **Webhooks** : notifications d'integration (stock bas, sang expirant, reaction transfusionnelle)

### Roles RBAC

| Role | Description |
|------|-------------|
| `admin` | Administrateur systeme |
| `medecin` | Medecin prescripteur |
| `infirmier` | Infirmier(e) administrant les transfusions |
| `technicien_labo` | Technicien de laboratoire |
| `efs_agent` | Agent de l'Etablissement Francais du Sang |

### Stack technique

- **Backend** : FastAPI (Python), PostgreSQL 15, Redis 7
- **Frontend** : React, Vite, Tailwind CSS
- **Monorepo** : pnpm + Turborepo
- **Conteneurisation** : Docker Compose

## Demarrage rapide

```bash
# Demarrer les services Docker (PostgreSQL, Redis)
docker-compose up -d

# Installer les dependances frontend
pnpm install

# Demarrer le backend
pnpm dev:backend

# Demarrer le frontend
pnpm dev:web
```

### Ports

| Service | Port |
|---------|------|
| Frontend (web) | 3700 |
| Backend (API) | 9400 |
| PostgreSQL | 5432 |
| Redis | 6379 |

## Structure du projet

```
bloodtrace/
  backend/          # API FastAPI Python
  apps/web/         # Application React + Vite + Tailwind
  packages/
    types/          # Types TypeScript partages
    utils/          # Utilitaires partages
    ui/             # Composants UI reutilisables
    api-client/     # Client API
    theme/          # Configuration du theme
    integration/    # Integration SIH (FHIR, Webhooks)
```

## Integration SIH

### Endpoints FHIR

- `GET /api/fhir/Patient/{ipp}` - Recuperer un patient par IPP
- `GET /api/fhir/Specimen/{id}` - Recuperer un specimen (poche de sang)
- `POST /api/fhir/ServiceRequest` - Creer une demande de service

### Webhooks

BloodTrace emet des evenements webhook pour l'integration :

- `low_stock` - Niveau de stock critique pour un type sanguin
- `expiring_blood` - Poches de sang proches de la date de peremption
- `transfusion_reaction` - Reaction transfusionnelle signalee
