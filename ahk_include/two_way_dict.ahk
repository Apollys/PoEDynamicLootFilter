Class TwoWayDict {
	forward_dict := {}
	reverse_dict := {}

	__New(input_dict_or_array) {
		this.forward_dict := input_dict_or_array
		for key, value in input_dict_or_array {
			this.reverse_dict[value] := key
		}
	}

	GetValue(key) {
		return this.forward_dict[key]
	}

	GetKey(value) {
		return this.reverse_dict[value]
	}
}
