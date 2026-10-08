# Evidencia de Configuración — Branch Protection sobre `master`

**Fecha:** 2026-10-07
**Repositorio:** `MajoLvR16/tickethelp-audit-stabilization`
**Rama protegida:** `master`
**Ejecutado por:** María José López Reyes (vía GitHub CLI, `gh api`), con permisos `ADMIN` confirmados sobre el repositorio.

## Contexto

Hallazgo de auditoría pendiente (controles de acceso y seguridad de la gestión de la configuración): la rama `master` del monorepo no tenía ninguna protección configurada, permitiendo push directo sin revisión y sin pasar por Pull Request, incluso para el propietario del repositorio.

## 1. Estado ANTES de la configuración

**Comando:**
```
gh api repos/MajoLvR16/tickethelp-audit-stabilization/branches/master/protection
```

**Respuesta:** `404 Not Found`
```json
{
  "message": "Branch not protected",
  "documentation_url": "https://docs.github.com/rest/branches/branch-protection#get-branch-protection",
  "status": "404"
}
```

Confirmado: no existía ninguna regla de protección sobre `master` antes de esta intervención.

## 2. Configuración aplicada

**Comando:**
```
gh api repos/MajoLvR16/tickethelp-audit-stabilization/branches/master/protection \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  --input - <<'EOF'
{
  "required_status_checks": null,
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 0
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF
```

**Justificación de los valores elegidos:**
- `required_pull_request_reviews` con `required_approving_review_count: 0`: exige que todo cambio a `master` pase por un Pull Request (no push directo), sin exigir un segundo revisor humano — razonable para un proyecto de ejecución unipersonal.
- `required_status_checks: null`: no se configuró ningún check de CI obligatorio porque no existe ningún pipeline de CI configurado en este repositorio al momento de esta intervención. No se inventó ni simuló uno.
- `enforce_admins: true`: la protección aplica también al propietario del repositorio, sin excepciones.
- `restrictions: null`: no se restringe qué usuarios/equipos pueden hacer push (no aplica en un repositorio unipersonal).
- `allow_force_pushes: false`, `allow_deletions: false`: se bloquean force-push y borrado de la rama `master`.

## 3. Estado DESPUÉS de la configuración (verificación)

**Comando:**
```
gh api repos/MajoLvR16/tickethelp-audit-stabilization/branches/master/protection
```

**Respuesta (200 OK):**
```json
{
    "url": "https://api.github.com/repos/MajoLvR16/tickethelp-audit-stabilization/branches/master/protection",
    "required_pull_request_reviews": {
        "url": "https://api.github.com/repos/MajoLvR16/tickethelp-audit-stabilization/branches/master/protection/required_pull_request_reviews",
        "dismiss_stale_reviews": false,
        "require_code_owner_reviews": false,
        "require_last_push_approval": false,
        "required_approving_review_count": 0
    },
    "required_signatures": {
        "url": "https://api.github.com/repos/MajoLvR16/tickethelp-audit-stabilization/branches/master/protection/required_signatures",
        "enabled": false
    },
    "enforce_admins": {
        "url": "https://api.github.com/repos/MajoLvR16/tickethelp-audit-stabilization/branches/master/protection/enforce_admins",
        "enabled": true
    },
    "required_linear_history": {
        "enabled": false
    },
    "allow_force_pushes": {
        "enabled": false
    },
    "allow_deletions": {
        "enabled": false
    },
    "block_creations": {
        "enabled": false
    },
    "required_conversation_resolution": {
        "enabled": false
    },
    "lock_branch": {
        "enabled": false
    },
    "allow_fork_syncing": {
        "enabled": false
    }
}
```

`required_status_checks` y `restrictions` no aparecen en la respuesta (ambos quedaron en `null`, tal como se configuró), confirmando que no se simuló ningún check de CI inexistente ni ninguna restricción de usuarios.

## 4. Resumen

| Aspecto | Antes | Después |
|---|---|---|
| Protección sobre `master` | Ninguna (404) | Activa (200) |
| Push directo a `master` (incluido el propietario) | Permitido | Bloqueado — requiere Pull Request |
| Force-push a `master` | Permitido | Bloqueado |
| Borrado de `master` | Permitido | Bloqueado |
| Checks de CI obligatorios | N/A | Ninguno configurado (no existe CI en este repositorio) |
