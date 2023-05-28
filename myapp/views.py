from django.shortcuts import redirect


def home_admin(request):
    print("lala")
    return redirect("admin/")