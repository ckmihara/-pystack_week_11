from django.shortcuts import render, redirect
from .models import Empresas, Documento, Metricas
from investidores.models import PropostaInvestimento
from django.contrib import messages
from django.contrib.messages import constants

# Create your views here.
def cadastrar_empresa(request):
    if not request.user.is_authenticated :
        return redirect('/usuarios/logar/')

    if request.method == "GET":
        return render(request, 'cadastrar_empresa.html', 
                      {'tempo_existencia': Empresas.tempo_existencia_choices,  
                       'areas': Empresas.area_choices}                      
                      )
    elif request.method == "POST":
        nome = request.POST.get('nome')
        cnpj = request.POST.get('cnpj')
        site = request.POST.get('site')
        tempo_existencia = request.POST.get('tempo_existencia')
        descricao = request.POST.get('descricao')
        data_final = request.POST.get('data_final')
        percentual_equity = request.POST.get('percentual_equity')
        estagio = request.POST.get('estagio')
        area = request.POST.get('area')
        publico_alvo = request.POST.get('publico_alvo')
        valor = request.POST.get('valor')
        pitch = request.FILES.get('pitch')
        logo = request.FILES.get('logo')

        try:
            empresa = Empresas(
                user=request.user,
                nome=nome,
                cnpj=cnpj,
                site=site,
                tempo_existencia=tempo_existencia,
                descricao=descricao,
                data_final_captacao=data_final,
                percentual_equity=percentual_equity,
                estagio=estagio,
                area=area,
                publico_alvo=publico_alvo,
                valor=valor,
                pitch=pitch,
                logo=logo
            )
            empresa.save()
        except:
            messages.add_message(request, constants.ERROR, 'Erro interno do sistema')
            return redirect('/empresarios/cadastrar_empresa')
        
        messages.add_message(request, constants.SUCCESS, 'Empresa criada com sucesso')
        return redirect('/empresarios/cadastrar_empresa')

def listar_empresas(request):

    if not request.user.is_authenticated :
        return redirect('/usuarios/logar/')
    
    if request.method == "GET":
        #TO DO Realizar o filtro das empresas
        empresas = Empresas.objects.filter(user=request.user)
        # print(empresas)
        return render(request, 'listar_empresas.html', {'empresas': empresas})
    
def empresa(request, id):
    empresa = Empresas.objects.get(id=id)
    if empresa.user != request.user :
        messages.add_message(request, constants.ERROR, "Esta empresa não é sua !!!!")
        return redirect(f'/empresarios/listar_empresas')
    
    if request.method == "GET":
        documentos = Documento.objects.filter(empresa=empresa)
        percentual_vendido = 0

        for pi in proposta_investimentos:
            if pi.status == 'PA':
                percentual_vendido += pi.percentual

        total_captado = sum(proposta_investimentos.filter(status='PA').values_list('valor', flat=True))
        
        valuation_atual = (100 * float(total_captado)) / float(percentual_vendido) if percentual_vendido != 0 else 0

        proposta_investimentos = PropostaInvestimento.objects.filter(empresa=empresa)
        proposta_investimentos_enviada = proposta_investimentos.filter(status='PE')
        return render(request, 'empresa.html', {'empresa': empresa, 'documentos': documentos, 'proposta_investimentos_enviada': proposta_investimentos_enviada, 'percentual_vendido': int(percentual_vendido), 'total_captado': total_captado, 'valuation_atual': valuation_atual})

def add_doc(request, id):
    empresa = Empresas.objects.get(id=id)
    titulo = request.POST.get('titulo')
    arquivo = request.FILES.get('arquivo')
    

    if empresa.user != request.user :
        messages.add_message(request, constants.ERROR, "Esta empresa não é sua !!!!")
        return redirect(f'/empresarios/listar_empresas')
    
    if not arquivo:
        messages.add_message(request, constants.ERROR, "Envie um arquivo")
        return redirect(f'/empresarios/empresa/{empresa.id}')
    
    if len(titulo) == 0:
            messages.add_message(request, constants.ERROR, "Título obrigatório")
            return redirect(f'/empresarios/empresa/{empresa.id}')
    
    extensao = arquivo.name.split('.')
    if extensao[1] != 'pdf':
            messages.add_message(request, constants.ERROR, "Envie apenas PDF's")
            return redirect(f'/empresarios/empresa/{empresa.id}')
        
    documento = Documento(
        empresa=empresa,
        titulo=titulo,
        arquivo=arquivo
    )
    documento.save()
    messages.add_message(request, constants.SUCCESS, "Arquivo cadastrado com sucesso")
    return redirect(f'/empresarios/empresa/{empresa.id}')

def excluir_dc(request, id):

    documento = Documento.objects.get(id=id)

    if documento.empresa.user != request.user:
        messages.add_message(request, constants.ERROR, "Esse documento não é seu")
        return redirect(f'/empresarios/empresa/{empresa.id}')

    documento = Documento.objects.get(id=id)
    documento.delete()
    messages.add_message(request, constants.SUCCESS, "Documento excluído com sucesso")
    return redirect(f'/empresarios/empresa/{documento.empresa.id}')

def add_metrica(request, id):
    empresa = Empresas.objects.get(id=id)
    titulo = request.POST.get('titulo')
    valor = request.POST.get('valor')
    
    metrica = Metricas(
        empresa=empresa,
        titulo=titulo,
        valor=valor
    )
    metrica.save()

    messages.add_message(request, constants.SUCCESS, "Métrica cadastrada com sucesso")
    return redirect(f'/empresarios/empresa/{empresa.id}')

def gerenciar_proposta(request, id):
    acao = request.GET.get('acao')
    pi = PropostaInvestimento.objects.get(id=id)

    if acao == 'aceitar':
        messages.add_message(request, constants.SUCCESS, 'Proposta aceita')
        pi.status = 'PA'
    elif acao == 'recusar':
        messages.add_message(request, constants.SUCCESS, 'Proposta recusada')
        pi.status = 'PR'


    pi.save()
    return redirect(f'/empresarios/empresa/{pi.empresa.id}')

def validacao_cnpj(cnpj):
    """Função para validar o CNPJ.
       Retorna True ou False
    """

    # Remove caracteres não numéricos do CNPJ
    cnpj = ''.join(filter(str.isdigit, cnpj))

    # Verifica se o CNPJ tem 12 dígitos (sem os verificadores)
    if len(cnpj) != 14:
        return False
    else :
        cnpj_calculado = cnpj[:-2]

    # Cálculo do primeiro dígito verificador
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma1 = 0
    for i in range(12):
        soma1 += int(cnpj_calculado[i]) * pesos1[i]
    digito1 = 11 - (soma1 % 11)
    digito1 = 0 if digito1 >= 10 else digito1

    # Cálculo do segundo dígito verificador
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma2 = 0
    for i in range(13):
        soma2 += int(cnpj_calculado[i] if i < 12 else str(digito1)) * pesos2[i]
    digito2 = 11 - (soma2 % 11)
    digito2 = 0 if digito2 >= 10 else digito2
    
    if cnpj == cnpj_calculado + str(digito1) + str(digito2) :
        return True
    else :
        return False