from django.shortcuts import render
from django.http import HttpResponse
import io
from base64 import b64decode, b64encode
from django.http import JsonResponse
import copy
def index(request):
	return render(request, 'afwk/index.html', {})


def classify(request):
	global reverso, probabilistico, V, compl, K, s0, F, transiciones
	if request:
		reverso, probabilistico, V, compl, K, s0, F, transiciones = load(request.GET.get('text', None))
	stateless = K == [s0] and F == [s0]
	all_final = len(K) == len(F) and all([k in F for k in K])
	simple = all([len(t[1]) == 0 or len(t[2]) == 0 for t in transiciones])
	limitado = all([len(t[1]) + len(t[2]) == 1 for t in transiciones])
	transText = ""
	i = 0
	for t in transiciones:
		transText += ("<tr class='transicion'>" if i%2==0 else "") + "<td><span class='middle'>δ</span><span class='par'>(</span><table class='tablaTransicion'><tbody><tr><td rowspan='2'>"
		transText += t[0] + ", <span class='par2'>(</span></td><td>"
		if len(t[1]) == 0:
			transText += "λ"
		else:
			for sim in t[1]:
				transText += sim
		transText += "</td></tr><tr><td>"
		if len(t[2]) == 0:
			transText += "λ"
		else:
			for sim in t[2]:
				transText += sim
		transText += "</td></tr></tbody></table><span class='par2'>)</span><span class='par'>)</span><span class='middle'> = {"
		notPrim = False
		for dest in t[3]:
			if notPrim:
				transText += ", "
			else:
				notPrim = True
			if probabilistico:
				transText += "(" + dest[0] + ", " + dest[1] + ")"
			else:
				transText += dest[0]
		transText += "}</span></td>" + ("</tr>" if i%2==1 else "")
		i+=1
	data = {
		'stateless': stateless,
		'all_final': all_final,
		'simple': simple,
		'limitado': limitado,
		'V': str(V).replace("[", "{").replace("]", "}").replace("'", ""),
		'compl': "{" + str(compl)[1:-1].replace("[", "(").replace("]", ")").replace("'", "") + "}",
		'K': str(K).replace("[", "{").replace("]", "}").replace("'", ""),
		"s0": str(s0),
		'F': str(F).replace("[", "{").replace("]", "}").replace("'", ""),
		"rev": reverso,
		"prob": probabilistico,
		"transiciones": transText
	}
	return JsonResponse(data)

def load(text):
	content = text.split("\n")
	assert len(content) > 7, "La especificación del autómata tiene que tener por lo menos 6 líneas (Tipo (N/R), Probabilistico (N/P), V, gamma, K, s0, F, delta)"
	assert content[0].strip() == "N" or content[0].strip() == "R", "El AFWK solo puede ser normal (N) o reverso (R)"
	tipo = content[0].strip()
	assert content[1].strip() == "N" or content[1].strip() == "P", "El AFWK solo puede ser normal (N) o probabilístico (P)"
	probabilistico = content[1].strip()
	V = content[2].strip().replace(" ", "").split(",")
	compl = [c.split(",") for c in content[3].strip().replace(" ", "").split(";")]
	assert set([c[0] for c in compl] + [c[1] for c in compl]) == set(V), "La función de complementariedad tiene que especificar 1 complementario para cada símbolo de V"
	K = content[4].strip().replace(" ", "").split(",")
	s0 = content[5].strip().replace(" ", "")
	assert s0 in K, "El estado inicial debe pertenecer a K"
	F = content[6].strip().replace(" ", "").split(",")
	assert all([f in K for f in F]), "Todos los estados finales deben pertenecer a K"
	transiciones = []
	for i in range(7, len(content)):
		if len(content[i].strip()) == 0:
			continue
		trans = content[i].strip().split(";")
		assert len(trans) == 4, "Transición (" + content[i].strip() + ") mal formada"
		so = trans[0].replace(" ", "")
		assert so in K, "El estado origen de la transición (" + content[i].strip() + ") no pertenece a K"
		hs = trans[1].replace(" ", "").split(",") if trans[1] != "" else []
		assert all([s in V for s in hs]), "Alguno de los símbolos de la hebra superior de la transición (" + content[i].strip() + ") no pertenece a V"
		hi = trans[2].replace(" ", "").split(",") if trans[2] != "" else []
		assert all([s in V for s in hi]), "Alguno de los símbolos de la hebra inferior de la transición (" + content[i].strip() + ") no pertenece a V"
		sd = trans[3].replace(" ", "").split(",")
		if probabilistico ==  "P":
			sd = [tuple(s.split("|")) for s in sd]
			assert all([len(s)==2 for s in sd]), "Las probabilidades no están bien especificadas en la transición (" + content[i].strip() + ")"
		else:
			sd = [tuple([s, 1]) for s in sd]
		assert all([s[0] in K for s in sd]), "Alguno de los estados destino de la transición (" + content[i].strip() + ") no pertenece a K"
		transiciones.append([so, hs, hi, sd])
		
	return tipo == "R", probabilistico == "P", V, compl, K, s0, F, transiciones


def convertir(request):
	global reverso, probabilistico, V, compl, K, s0, F, transiciones

	i = 0
	nuevoEst = "qaux"
	nuevasTransiciones = []
	for t in transiciones:
		nuevaTransicion = [t[0]]
		for s in t[1]:
			nuevaTransicion.append(s)
			nuevaTransicion.append(None)
			nuevaTransicion.append([(nuevoEst+str(i),"1")])
			nuevasTransiciones.append(nuevaTransicion[:])
			nuevaTransicion = [nuevoEst+str(i)]
			i += 1
		for s in t[2]:
			nuevaTransicion.append(None)
			nuevaTransicion.append(s)
			nuevaTransicion.append([(nuevoEst+str(i),"1")])
			nuevasTransiciones.append(nuevaTransicion[:])
			nuevaTransicion = [nuevoEst+str(i)]
			i += 1
		i -= 1
		nuevasTransiciones[-1][3] = t[3]
	
	for s in K:
		trans = [t for t in nuevasTransiciones if t[0] == s]
		simbolosHS = set([t[1] for t in trans if t[1] is not None])
		for simbolo in simbolosHS:
			ts = [t for t in trans if t[1]==simbolo]
			sf = []
			for t in ts:
				sf += t[3]
				nuevasTransiciones.remove(t)
			nuevasTransiciones.append([s, simbolo, None, sf])
		simbolosHI = set([t[2] for t in trans if t[2] is not None])
		for simbolo in simbolosHI:
			ts = [t for t in trans if t[2]==simbolo]
			sf = []
			for t in ts:
				sf += t[3]
				nuevasTransiciones.remove(t)
			nuevasTransiciones.append([s, None, simbolo, sf])

	for j in range(i):
		K.append(nuevoEst+str(j))
	
	transiciones = [[t[0], [t[1]] if t[1] else [], [t[2]] if t[2] else [], t[3]] for t in nuevasTransiciones]
	if request:
		return classify(None)

def descargar(request):
	global reverso, probabilistico, V, compl, K, s0, F, transiciones
	print(request)
	outname = request.GET.get('filename', None)
	with open(outname, "w") as f:
		f.write(("R" if reverso else "N") + "\n")
		f.write(("P" if probabilistico else "N") + "\n")
		f.write(",".join(V) + "\n")
		f.write(";".join([",".join(c) for c in compl]) + "\n")
		f.write(",".join(K)+"\n")
		f.write(s0 + "\n")
		f.write(",".join(F) + "\n")
		for trans in transiciones:
			if probabilistico:
				dest = ["|".join(t) for t in trans[3]]
				dest = ",".join(dest)
			else:
				dest = ",".join([t[0] for t in trans[3]])
			f.write(
				trans[0] + ";" +
				(",".join(trans[1]) if len(trans[1]) != 0 else "") + ";" +
				(",".join(trans[2]) if len(trans[2]) != 0 else "") + ";" +
				dest + "\n"
			)
			
	with open(outname) as myfile:
		response = HttpResponse(myfile.read(), content_type='text/txt')
		response['Content-Disposition'] = 'attachment; filename="'+outname+'"'
		return response

def analizar(request):
	global reverso, probabilistico, V, compl, K, s0, F, transiciones
	word = request.GET.get('word', None)
	lower_word = ""
	for l in word:
		for c in compl:
			if l == c[0]:
				lower_word += c[1]
			elif l == c[1]:
				lower_word += c[0]
	if reverso:
		lower_word = lower_word[::-1]
		
	transicionesViejas = copy.deepcopy(transiciones)

	for t in transiciones:
		t[0] = K.index(t[0])
		t[1] = t[1][0] if len(t[1]) > 0 else None
		t[2] = t[2][0] if len(t[2]) > 0 else None
		t[3] = [(K.index(s[0]), float(s[1])) for s in t[3]]

	trellis = [[[(0., "") for i in range(len(K))] for i in range(len(word)+1)] for i in range(len(word)+1)]
	
	trellis[0][0][K.index(s0)] = (1., "")

	for i in range(len(word)+1):
		for j in range(len(word)+1):
			for k in range(len(K)):
				if trellis[i][j][k][0] > 0:
					if i == len(word) and j == len(word):
						break
					if i == len(word):
						ts = [t for t in transiciones if t[0]==k and t[2] == lower_word[j]]
					elif j == len(word):
						ts = [t for t in transiciones if t[0]==k and t[1] == word[i]]
					else:
						ts = [t for t in transiciones if t[0]==k and (t[1] == word[i] or t[2] == lower_word[j])]
					for trans in [t for t in ts if t[2] is None]:
						for s in trans[3]:
							if s[1] * trellis[i][j][k][0] > trellis[i+1][j][s[0]][0]:
								trellis[i+1][j][s[0]] = (s[1] * trellis[i][j][k][0], trans[:3])
					for trans in [t for t in ts if t[1] is None]:                            
						for s in trans[3]:
							if s[1] * trellis[i][j][k][0] > trellis[i][j+1][s[0]][0]:
								trellis[i][j+1][s[0]] = (s[1] * trellis[i][j][k][0], trans[:3])
								
	probabilidad = 0
	actual = 0
	for s in F:
		ind = K.index(s)
		if trellis[-1][-1][ind][0] > probabilidad:
			probabilidad = trellis[-1][-1][ind][0]
			actual = ind
	secuencia = []
	i = len(word)
	j = len(word)
	while (i > 0 or j > 0) and probabilidad > 0:
		transicion = trellis[i][j][actual][1] + [K[actual]]
		actual = transicion[0]
		transicion[0] = K[transicion[0]]
		secuencia.append(transicion)
		if transicion[1] is None:
			j -= 1
			transicion[1] = "λ"
		else:
			i -= 1
			transicion[2] = "λ"
	secuencia.reverse()
	transiciones = transicionesViejas
	
	data = {
		'probabilistico': probabilistico,
		'acepta': probabilidad > 0,
		'probabilidad': probabilidad,
		'secuencia': secuencia,
		'complementaria': lower_word,
		'reverso': reverso,
		'trellis': trellis
	}
	for t in trellis:
		print(t)
	return JsonResponse(data)