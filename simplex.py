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
	col_dim = 0
	row_dim = 0

	def __init__(self, input_file):
		self.input_file_name = input_file.split('.')[0]
		self.read_input(input_file)
		if self.method == "1":
			print("tabular_simplex")
			self.tabular_simplex()
		else:
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
		self.to_equations(self.equations)
		
		#creo la lista de VB
		self.vb = self.create_vb_list()

		#creo la tabla
		table = [self.U_vars];
		table.extend(self.equations)

		while(True):
			#calculo los pivotes
			column_pivot = self.get_column_pivot(table)
			if column_pivot == -1:
				self.write_file(table, -1, -1, -1)
				break
			row_pivot = self.get_row_pivot(table, column_pivot)
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

	def to_equations(self, inequalities):
		for i in range(0, len(inequalities)):
			split_inequalities = inequalities[i].split(",")
			equation = [0.0] * (self.n_vars + self.n_restrictions + 1)
			for j in range(0,self.n_vars):
				equation[j] = float(split_inequalities[j])
			if(split_inequalities[self.n_vars] == "<="):
				equation[self.n_vars+i] = 1.0;
			elif(split_inequalities[self.n_vars] == ">="):
				equation[self.n_vars+i] = -1.0
			else: 
				equation[self.n_vars+i] = 0.0
			equation[len(equation)-1] = float(split_inequalities[self.n_vars+1])
			self.equations[i] = equation

	def create_vb_list(self):
		vb = ["U"]
		for i in range(0,self.n_restrictions):
			vb.append("X"+str(i+self.n_vars))
		return vb

	def get_column_pivot(self, table):
		min_val = INF
		column = -1
		for j in range(len(table[0])):
			if(table[0][j] < min_val):
				min_val = table[0][j]
				column = j
		if(min_val >= 0):
			return -1
		return column

	def get_row_pivot(self, table, piv):
		min_val = INF
		row = -1
		for i in range(0, len(table)):
			if(table[i][self.col_dim-1] and table[i][self.col_dim-1]/table[i][piv] < min_val):
				min_val = table[i][self.col_dim-1]/table[i][piv]
				row = i
		return row

	def get_next_table(self, table, column_pivot, row_pivot, pivot):
		new_table = copy.deepcopy(table)
		new_vb = self.vb.copy()
		new_vb[row_pivot] = "X"+str(column_pivot)
		for j in range(0, self.col_dim):
			new_table[row_pivot][j] /= pivot

		for i in range(0, self.row_dim):
			if(i != row_pivot):
				for j in range(0, self.col_dim):
					new_table[i][j] = new_table[row_pivot][j]*table[i][column_pivot]
					new_table[i][j] = table[i][j] - new_table[i][j]
		return new_table, new_vb

	def write_file(self,table, column_pivot, row_pivot, pivot):
		f = open(self.input_file_name+"_solucion.txt", 'a')
		first_line = "VB    "
		for i in range(0, self.col_dim-1):
			first_line += "X"+str(i)+"    "
		first_line += "LD" 
		f.write(first_line+"\n")
		for i in range(0, len(self.vb)):
			f.write(str(self.vb[i])+"   ")
			for j in range(0, self.col_dim):
				f.write("{:.4f}".format(table[i][j])+"   ")
			f.write("\n")
		if(column_pivot != -1):
			f.write("VB entrante: X"+str(column_pivot))
			f.write(" VB saliente: "+self.vb[row_pivot])
			f.write(" Numero pivote: "+"{:.4f}".format(pivot))
		else:
			f.write("Estado optimo")
		f.write("\nRespuesta Parcial: U = "+"{:.4f}".format(table[0][self.col_dim-1]))
		f.write(", (")
		for i in range(0,self.n_vars):
			X = self.vb.index("X"+str(i)) if "X"+str(i) in self.vb else None
			if X == None:
				f.write("0, ")
			else:
				f.write(str(table[X][self.col_dim-1])+", ")
		for i in range(1, self.n_restrictions):
			f.write(str(table[i][self.col_dim-1])+", ")
		f.write(str(table[self.n_restrictions][self.col_dim-1]))
		f.write(")\n\n")
		f.close()

	def two_phases(self):
		pass

	def to_string(self):
		print(self.method)
		print(self.opt)
		print(self.n_vars)
		print(self.n_restrictions)
		print(self.U_vars)
		print(self.equations)


simplex = Simplex(sys.argv[1])
#simplex.to_string()