import azimuthal_average.data.data_types as data_types

if __name__ == "__main__":
    "Test vectors"
    velocity_cartesian_vector = data_types.CartesianVector([1, 2, 3])
    r_vector = data_types.CartesianVector([3, -2, 1])
    velocity_cylindrical_vector = velocity_cartesian_vector.convert_to_cylindrical(r_vector)
    print(velocity_cylindrical_vector)

    "Test tensors"
    symm_cartesian_tensor_array = [1, 2, 3, 4, 5, 6]
    symm_cartesian_tensor = data_types.SymmetricCartesianTensor(symm_cartesian_tensor_array)
    for component in data_types.SymmetricCartesianTensor.list_of_components:
        print(f"T_{component} =", getattr(symm_cartesian_tensor, component))

    symm_cylindrical_tensor = symm_cartesian_tensor.convert_to_cylindrical(r_vector)

    for component in data_types.SymmetricCylindricalTensor.list_of_components:
        print(f"R_{component} =", getattr(symm_cylindrical_tensor, component))
    print(symm_cylindrical_tensor)