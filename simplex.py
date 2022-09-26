import sys
import copy

INF = 100000000000000.0

class Simplex():
	input_file_name = ""
	method = 0;
	opt = 0
	n_vars = 0
	n_restrictions = 0
	U_vars = []
	equations = []
	vb = []
	artificial_vars = []
	slack_vars = []
	col_dim = 0
	row_dim = 0

	def __init__(self, input_file):
		self.input_file_name = input_file.split('.')[0]
		self.read_input(input_file)
		if self.method == "1":
			print("tabular_simplex")
			self.tabular_simplex()
		else:
			print("two phases")
			self.two_phases()

	def read_input(self, input_file):
		with open(input_file,'r') as file:
			line = file.readline()
			line = line.split(',')
			self.method = line[0]
			self.opt = line[1]
			self.n_vars = int(line[2])
			self.n_restrictions = int(line[3])
			self.row_dim = self.n_restrictions+1
			self.col_dim = self.n_vars + self.n_restrictions + 1

			line = file.readline()
			line = line.split(',')
			for i in line:
				self.U_vars.append(float(i))

			equations = []
			line = file.readline()
			while line:
				self.equations.append(line)
				line = file.readline()

	def tabular_simplex(self):
		#despejo U
		self.U_vars = self.clear_u(self.U_vars)

		#convetir las inecuaciones en ecuaciones
		self.to_equations_tabular(self.equations)
		
		#creo la lista de VB
		self.vb = self.create_vb_list()

		#creo la tabla
		table = [self.U_vars];
		table.extend(self.equations)

		while(True):
			print("enter to next")
			input()
			#calculo los pivotes
			column_pivot = self.get_column_pivot(table, self.method)
			if column_pivot == -1:
				self.write_file(table, -1, -1, -1)
				break
			row_pivot = self.get_row_pivot(table, column_pivot, self.col_dim)
			pivot = table[row_pivot][column_pivot]

			# escribir en el archivo la tabla pa guardar el paso
			self.write_file(table, column_pivot, row_pivot, pivot)

			#hago el nuevo paso y escribo actualizo tabla
			table, self.vb = self.get_next_table(table, column_pivot, row_pivot, pivot)
	
	def clear_u(self, U_vars):
		for i in range(0, len(U_vars)):
			U_vars[i] *= -1
		for i in range(0,self.row_dim):
			U_vars.append(0.0)
		return U_vars

	def to_equations_tabular(self, inequalities):
		#solo recibe inecuaciones de <= ya que es tabular
		for i in range(0, len(inequalities)):
			split_inequalities = inequalities[i].split(",")
			equation = [0.0] * (self.n_vars + self.n_restrictions + 1)
			for j in range(0,self.n_vars):
				equation[j] = float(split_inequalities[j])
		
			equation[self.n_vars+i] = 1.0;
			equation[len(equation)-1] = float(split_inequalities[self.n_vars+1])

			print("inequalities")
			print(len(inequalities))
			print(i)
			self.equations[i] = equation

	def create_vb_list(self):
		vb = ["U"]
		for i in range(0,self.n_restrictions):
			vb.append("X"+str(i+self.n_vars))
		return vb

	def get_column_pivot(self, table, method):
		if(method == "max"):
			min_val = INF
			column = -1
			for j in range(len(table[0])-1):
				if(table[0][j] < min_val):
					min_val = table[0][j]
					column = j
			if(min_val >= 0):
				return -1
		else:
			max_val = -INF
			column = -1
			for j in range(len(table[0])-1):
				if(table[0][j] > max_val):
					max_val = table[0][j]
					column = j
			if(max_val <= 0):
				return -1

		return column

	def get_row_pivot(self, table, piv, col_dimension):
		min_val = INF
		row = -1
		for i in range(1, len(table)):
			if(table[i][col_dimension-1] >= 0):
				if(table[i][piv] >0 and table[i][col_dimension-1]/table[i][piv] < min_val):
					min_val = table[i][col_dimension-1]/table[i][piv]
					row = i
		return row

	def get_next_table(self, table, column_pivot, row_pivot, pivot):
		new_table = copy.deepcopy(table)
		new_vb = self.vb.copy()
		new_vb[row_pivot] = "X"+str(column_pivot)
		for j in range(0, len(table[0])):
			new_table[row_pivot][j] /= pivot

		for i in range(0, len(table)):
			if(i != row_pivot):
				for j in range(0, len(table[0])):
					new_table[i][j] = new_table[row_pivot][j]*table[i][column_pivot]
					new_table[i][j] = table[i][j] - new_table[i][j]
		return new_table, new_vb

	def write_file(self,table, column_pivot, row_pivot, pivot):
		f = open(self.input_file_name+"_solucion.txt", 'a')
		first_line = "VB    "
		for i in range(0, len(table[0])-1):
			first_line += "X"+str(i)+"    "
		first_line += "LD" 
		f.write(first_line+"\n")
		for i in range(0, len(self.vb)):
			f.write(str(self.vb[i])+"   ")
			for j in range(0, len(table[0])):
				f.write("{:.4f}".format(table[i][j])+"   ")
			f.write("\n")
		if(column_pivot != -1):
			f.write("VB entrante: X"+str(column_pivot))
			f.write(" VB saliente: "+self.vb[row_pivot])
			f.write(" Numero pivote: "+"{:.4f}".format(pivot))
		else:
			f.write("Estado optimo")
		f.write("\nRespuesta Parcial: U = "+"{:.4f}".format(table[0][len(table[0])-1]))
		f.write(", (")
		for i in range(0,self.n_vars-1):
			X = self.vb.index("X"+str(i)) if "X"+str(i) in self.vb else None
			if X == None:
				f.write("0, ")
			else:
				f.write(str(table[X][len(table[0])-1])+", ")
		X = self.vb.index("X"+str(self.n_vars-1)) if "X"+str(self.n_vars-1) in self.vb else None
		if X == None:
			f.write("0")
		else:
			f.write(str(table[X][len(table[0])-1]))
		f.write(")\n\n")
		f.close()

	def two_phases(self):
		#hacer conversiones de las inecuaciones
		self.to_equations_2phases(self.equations)

		#convertir la funcion objetivo
		U_vars = [0.0] * (self.n_vars + self.n_restrictions*2 + 1)
		for i in self.artificial_vars:
			U_vars[i] = 1

		#creo las variables basicas
		vb_list = []
		vb_list.append("U")
		for i in self.slack_vars:
			vb_list.append("X"+str(i))
		for i in self.artificial_vars:
			vb_list.append("X"+str(i))
		print(vb_list)
		self.vb = vb_list

		#hacer la primer tabla
		table = [U_vars]
		table.extend(self.equations)
		for t in table:
			print(t)

		#ajustar la matriz 
		for i in range(0, len(self.artificial_vars)):
			for j in range(0,len(table[0])):
				table[0][j] -= table[len(self.slack_vars)+1+i][j]

		for j in range(0,len(table[0])):
			table[0][j] *= -1

		print("tabla ajustada")
		for t in table:
			print(t)
		
		#PHASE 1
		while(True):
			print("enter to next")
			input()

			column_pivot = self.get_column_pivot(table, self.method)
			if column_pivot == -1:
				self.write_file(table, -1, -1, -1)
				break

			row_pivot = self.get_row_pivot(table, column_pivot, len(table[0]))
			pivot = table[row_pivot][column_pivot]

			self.write_file(table, column_pivot, row_pivot, pivot)

			table, self.vb = self.get_next_table(table, column_pivot, row_pivot, pivot)

			for t in table:
				print(t)

		#drop artificials
		print("drops artificial")
		aux = table[0:self.n_vars + self.n_restrictions]# + table[self.n_vars + self.n_restrictions*2+1:]
		table = aux
		for i in range(0,len(table)):
			table[i] = table[i][0:self.n_vars + self.n_restrictions] + table[i][self.n_vars + self.n_restrictions*2:]
		for t in table:
			print(t)

		#colocar U de nuevo en la primer fila
		self.U_vars = self.clear_u(self.U_vars)
		for x in range(0,len(self.U_vars)):
			table[0][x] = self.U_vars[x]


		#ajustar table si hace falta

		for i in range(0,self.n_vars):
			X = self.vb.index("X"+str(i)) if "X"+str(i) in self.vb else None
			print(str(X)+"row esta en la picha por X"+str(i))
			if X is not None:
				cons = (-1*table[0][i])
				for j in range(0, len(table[0])):
					print(str(table[0][j]) + " = "+str(cons) +" * "+str(table[X][j]))
					table[0][j] += cons * table[X][j]
		print("luego de ajsute")
		for t in table:
			print(t)
	
		self.write_file(table, -1, -1, -1)




		#hacer la primer tabla
		pass

	def to_equations_2phases(self, inequalities):
		for i in range(0, len(inequalities)):
			split_inequalities = inequalities[i].split(",")
			equation = [0.0] * (self.n_vars + self.n_restrictions*2 + 1)
			for j in range(0,self.n_vars):
				equation[j] = float(split_inequalities[j])
			if(split_inequalities[self.n_vars] == "<="):
				self.slack_vars.append(self.n_vars+i)
				equation[self.n_vars+i] = 1.0 #add slack
			elif(split_inequalities[self.n_vars] == "="):
				self.artificial_vars.append(self.n_vars+self.n_restrictions+i)
				equation[self.n_vars+self.n_restrictions+i] = 1.0 #add artifical
			else:
				equation[self.n_vars+i] = -1.0 #add sur
				self.artificial_vars.append(self.n_vars+self.n_restrictions+i)
				equation[self.n_vars+self.n_restrictions+i] = 1.0 #add artifical

			equation[len(equation)-1] = float(split_inequalities[self.n_vars+1])

			print("inequalities")
			print(len(inequalities))
			print(equation)
			self.equations[i] = equation

	def to_string(self):
		print(self.method)
		print(self.opt)
		print(self.n_vars)
		print(self.n_restrictions)
		print(self.U_vars)
		print(self.equations)


simplex = Simplex(sys.argv[1])
#simplex.to_string()