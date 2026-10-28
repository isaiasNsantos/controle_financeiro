def perfil_foto(request):
    if request.user.is_authenticated:
        # Tenta pegar o perfil do usuário logado
        try:
            perfil = request.user.perfil
            if perfil.foto:
                return {'foto_perfil_url': perfil.foto.url}
        except Exception:
            pass
    return {'foto_perfil_url': None}