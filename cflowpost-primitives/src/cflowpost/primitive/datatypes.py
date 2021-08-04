import numpy as np
import pandas as pd


def rotation_matrix(theta: float):
    return np.array(
        [[np.cos(theta), np.sin(theta), 0],
         [-np.sin(theta), np.cos(theta), 0],
         [0, 0, 1]]
    )


class VectorStack:
    components: tuple = ("i", "j", "k")

    def __init__(self, vector_array):
        self.__set_components(vector_array)
        self.array = np.array(vector_array)

    def __set_components(self, vector_array):
        comps = self.__class__.components
        for i, comp in enumerate(comps):
            setattr(self, comp, vector_array[:, i])

    def as_dataframe(self, prefix=""):
        comps = self.__class__.components
        columns = list(comps)
        if prefix:
            columns = [f"{prefix}_{column}" for column in columns]
        return pd.DataFrame(data=self.array, columns=columns)

    def __str__(self):
        return f"{self.array}"


class CartesianVectorStack(VectorStack):
    """Class for vectors in cartesian coordinates.

    Instance attributes:

    self.vector -- numpy array containing the vector
    self.x -- radial component
    self.y -- azimuthal component
    self.z -- axial component
    """
    components = ("x", "y", "z")

    def convert_to_cylindrical(self, theta):
        rot_matrix = rotation_matrix(theta)
        print(rot_matrix)
        cylindrical_vector_array = (rot_matrix.dot(self.array.T)).T
        return CylindricalVectorStack(cylindrical_vector_array)


class CylindricalVectorStack(VectorStack):
    """Class for vectors in cylindrical coordinates.

    Instance attributes:

    self.vector -- numpy array containing the vector
    self.r -- radial component
    self.t -- azimuthal component
    self.z -- axial component
    """
    components: tuple = ("r", "t", "z")


class SymmetricTensorStack:
    components: tuple = ("ii", "jj", "kk", "ij", "jk", "ik")

    def __init__(self, symm_tensor_array, ):
        self.__set_components(symm_tensor_array)
        self.tensor_stack = self.symm_tensor_array_to_tensor_stack(
            symm_tensor_array)

    def __set_components(self, symm_tensor_array):
        comps = self.__class__.components
        for i, comp in enumerate(comps):
            setattr(self, comp, symm_tensor_array[:, i])

    @staticmethod
    def tensor_stack_to_symm_array(tensor_stack):
        return np.array([tensor[np.triu_indices(3)] for tensor in tensor_stack])

    @staticmethod
    def symm_tensor_array_to_tensor_stack(symm_tensor_array):
        tensor_row_index = np.array([[0, 3, 5],
                                     [3, 1, 4],
                                     [5, 4, 2]])
        return np.array([tensor_row[tensor_row_index]
                         for tensor_row in symm_tensor_array])

    def symm_tensor_array(self):
        return self.tensor_stack_to_symm_array(self.tensor_stack)

    def as_dataframe(self, prefix=""):
        comps = self.__class__.components
        columns = list(comps)
        if prefix:
            columns = [f"{prefix}_{column}" for column in columns]
        symm_array = self.tensor_stack_to_symm_array(self.tensor_stack)
        return pd.DataFrame(data=symm_array, columns=columns)

    @staticmethod
    def _rotate_tensor_stack(tensor_stack, rotation_matrix_):
        return np.matmul(rotation_matrix_,
                         np.matmul(tensor_stack,
                                   rotation_matrix_.T))

    def rotate(self, theta: float):
        tensor_stack = self.tensor_stack
        rot_matrix = rotation_matrix(theta)
        return self._rotate_tensor_stack(tensor_stack, rot_matrix)


class SymmetricCartesianTensorStack(SymmetricTensorStack):
    components: tuple = ("xx", "yy", "zz", "xy", "yz", "xz")

    def convert_to_cylindrical(self, theta: float):
        cylindrical_tensor_stack = self.rotate(theta)
        return SymmetricCylindricalTensorStack(
            self.tensor_stack_to_symm_array(cylindrical_tensor_stack))


class SymmetricCylindricalTensorStack(SymmetricTensorStack):
    components = ("rr", "tt", "zz", "rt", "tz", "rz")
