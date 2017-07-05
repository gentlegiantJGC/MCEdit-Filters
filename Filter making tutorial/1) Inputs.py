# Made by gentlegiantJGC based on the demo filter that MCedit comes with
# https://www.youtube.com/gentlegiantJGC

# the inputs list tells MCEdit what kind of options to present to the user.
# each item is a (name, value) pair.  name is a text string acting
# both as a text label for the input on-screen and a key for the 'options'
# parameter to perform(). value and its type indicate allowable and
# default values for the option:

# displayName must be defined and is what the filter is called
displayName = "Name of the filter"

# inputs does not need to be defined but without it the filter will have no options
inputs = (
    ("random text", "label"), # This is a way to tell the user something without adding an input
	("True or False", (True)), # True or False: creates a checkbox with the given value as default
	("Int Value", (0)), # Int value: creates a value input with the given value as default. int values create fields that only accept integers.
	("Float Value", (0.0)), # Float value: creates a value input with the given value as default. Can be a decimal value.
	("Three Tuple", (4, -128, 128)), # Tuple of numbers: a tuple of ints or floats creates a value input with default, minimum and maximum values.
	("Two Tuple", (-128, 128)), # A 2-tuple specifies (min, max) with min as default.
	("String Tuple", ("option1", "option2", "option3", "...")), # Tuple of strings: creates a popup menu. The first item in the tuple is the default.
    ("Input String", ("string", "value=This is the default value")), #The first string is the name and everything after value= is the value. Don't change anything else
)


    # to put something on seperate tabs it will be need to be set up like this
inputs = [
    (
    ("this will be on the first tab", "label"),
    ("so will this", "label"),
    ),

    (
    ("this will be on the second tab", "label"),
    ("so will this", "label"),
    ),
    ]