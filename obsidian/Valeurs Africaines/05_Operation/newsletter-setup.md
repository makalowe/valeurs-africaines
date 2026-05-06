# Newsletter Provider Setup

## Mode recommande: Brevo + Substack

### 1) Brevo (capture + envoi)
Definir les variables d'environnement:
- BREVO_API_KEY=your_brevo_api_key
- BREVO_LIST_ID=123

### 2) Substack (canal editorial)
Definir:
- SUBSTACK_URL=https://votre-compte.substack.com

Le site affichera un lien direct Substack sur la page newsletter.

### 3) Flux operationnel combine
- Les emails saisis sur le site sont stockes localement.
- Si Brevo est configure, ils sont aussi pushes automatiquement vers Brevo.
- Depuis /admin, exporter les abonnes CSV puis importer dans Substack si besoin.
