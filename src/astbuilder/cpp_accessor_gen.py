from astbuilder.visitor import Visitor
from astbuilder.cpp_type_name_gen import CppTypeNameGen
from astbuilder.type_scalar import TypeKind
from astbuilder.type_pointer import PointerKind

class CppAccessorGen(Visitor):
    # Integer and pointer
    # - const read accessor
    # - non-const write-value accessor
    #
    # String
    # - const-ref read accessor
    # - non-const write accessor
    #
    # List, Map
    # - const-ref read accessor
    # - non-const write accessor
    #
    #
    
    def __init__(self, out_h, out_cpp, clsname):
        super().__init__()
        self.out_h = out_h
        self.out_cpp = out_cpp
        self.clsname = clsname
        self.field = None
        
    def gen(self, field):
        self.field = field
        
        self.field.t.accept(self)

    def visitTypeList(self, t):
        self.gen_collection_accessors(t)
    
    def visitTypeMap(self, t):
        self.gen_collection_accessors(t)
        
    def visitTypePointer(self, t):
        if t.pt == PointerKind.Raw:
            self.gen_rawptr_accessors(t)
        elif t.pt == PointerKind.Unique:
            self.gen_uptr_accessors(t)
        elif t.pt == PointerKind.Shared:
            self.gen_sptr_accessors(t)
        else:
            raise Exception("Accessor generation not supported for " + str(self.pt))

    def visitTypeScalar(self, t):
        if t.t == TypeKind.String:
            self.gen_string_accessors(t)
        else:
            self.gen_scalar_accessors(t)
    
    def gen_collection_accessors(self, t):
        # Generate a read-only accessor
        self.out_h.println(self.const_ref_ret(t) + "get_" + self.field.name + "() const;")
        self.out_h.println()

        self.out_cpp.println(self.const_ref_ret(t) + 
                             self.clsname + "::get_" + self.field.name + "() const {")
        self.out_cpp.inc_indent()
        self.out_cpp.println("return m_" + self.field.name + ";")
        self.out_cpp.dec_indent()
        self.out_cpp.println("}")
        self.out_cpp.println()
        
        # Generate a non-const accessor
        self.out_h.println(self.nonconst_ref_ret(t) + "get_" + self.field.name + "();")

        self.out_cpp.println(self.nonconst_ref_ret(t) + 
                             self.clsname + "::get_" + self.field.name + "() {")
        self.out_cpp.inc_indent()
        self.out_cpp.println("return m_" + self.field.name + ";")
        self.out_cpp.dec_indent()
        self.out_cpp.println("}")        
   
    def gen_scalar_accessors(self, t):
        # Generate a read-only accessor
        self.out_h.println(
            CppTypeNameGen(compressed=True,is_ret=True).gen(t) + 
            " get_" + self.field.name + "() const;")
        self.out_h.println()

        self.out_cpp.println(
            CppTypeNameGen(compressed=True,is_ret=True).gen(t) + 
                             " " + self.clsname + "::get_" + self.field.name + "() const {")
        self.out_cpp.inc_indent()
        self.out_cpp.println("return m_" + self.field.name + ";")
        self.out_cpp.dec_indent()
        self.out_cpp.println("}")
        self.out_cpp.println()
        
        # Generate a non-const accessor
        self.out_h.println("void set_" + self.field.name + "(" +
            CppTypeNameGen(compressed=True,is_ret=False).gen(t) + " v);")

        self.out_cpp.println("void " + self.clsname + "::set_" + self.field.name + 
                "(" + CppTypeNameGen(compressed=True,is_ret=False).gen(t) + " v) {")
        self.out_cpp.inc_indent()
        self.out_cpp.println("m_" + self.field.name + " = v;")
        self.out_cpp.dec_indent()
        self.out_cpp.println("}")
        
    def gen_rawptr_accessors(self, t):
        # Generate a read-only accessor
        self.out_h.println(
            CppTypeNameGen(compressed=True,is_ref=False,is_const=False).gen(t) + 
            "get_" + self.field.name + "();")
        self.out_h.println()

        self.out_cpp.println(
            CppTypeNameGen(compressed=True,is_const=False,is_ref=False).gen(t) + 
                            self.clsname + "::get_" + self.field.name + "() {")
        self.out_cpp.inc_indent()
        self.out_cpp.println("return m_" + self.field.name + ";")
        self.out_cpp.dec_indent()
        self.out_cpp.println("}")
        self.out_cpp.println()
        
        # Generate a setter
        self.out_h.println("void set_" + self.field.name + "(" +
            CppTypeNameGen(compressed=True,is_const=False,is_ref=False).gen(t) + "v);")

        self.out_cpp.println("void " + self.clsname + "::set_" + self.field.name + 
                "(" + CppTypeNameGen(compressed=True,is_const=False,is_ref=False).gen(t) + "v) {")
        self.out_cpp.inc_indent()
        self.out_cpp.println("m_" + self.field.name + " = v;")
        self.out_cpp.dec_indent()
        self.out_cpp.println("}") 
                       
    def gen_uptr_accessors(self, t):
        # Generate a read-only accessor
        self.out_h.println(
            CppTypeNameGen(compressed=True,is_ptr=True,is_const=False).gen(t.t) + 
            "get_" + self.field.name + "() const;")
        self.out_h.println()

        self.out_cpp.println(
            CppTypeNameGen(compressed=True,is_ptr=True,is_const=False).gen(t.t) + 
                            self.clsname + "::get_" + self.field.name + "() const {")
        self.out_cpp.inc_indent()
        self.out_cpp.println("return m_" + self.field.name + ".get();")
        self.out_cpp.dec_indent()
        self.out_cpp.println("}")
        self.out_cpp.println()
        
        # Generate a setter
        self.out_h.println("void set_" + self.field.name + "(" +
            CppTypeNameGen(compressed=True,is_const=False,is_ptr=True).gen(t.t) + "v);")

        self.out_cpp.println("void " + self.clsname + "::set_" + self.field.name + 
                "(" + CppTypeNameGen(compressed=True,is_const=False,is_ptr=True).gen(t.t) + "v) {")
        self.out_cpp.inc_indent()
        self.out_cpp.println("m_" + self.field.name + " = " + 
            CppTypeNameGen(compressed=True).gen(t) + "(v);")
        self.out_cpp.dec_indent()
        self.out_cpp.println("}")

    def gen_sptr_accessors(self, t):
        # Generate a read-only accessor
        self.out_h.println(
            CppTypeNameGen(compressed=True).gen(t) + " get_" + 
            self.field.name + "() const;")
        self.out_h.println()

        self.out_cpp.println(
            CppTypeNameGen(compressed=True).gen(t) + 
                            " " + self.clsname + "::get_" + self.field.name + "() const {")
        self.out_cpp.inc_indent()
        self.out_cpp.println("return m_" + self.field.name + ";")
        self.out_cpp.dec_indent()
        self.out_cpp.println("}")
        self.out_cpp.println()
        
        # Generate a setter
        self.out_h.println("void set_" + self.field.name + "(" +
            CppTypeNameGen(compressed=True).gen(t) + " v);")

        self.out_cpp.println("void " + self.clsname + "::set_" + self.field.name + 
                "(" + CppTypeNameGen(compressed=True).gen(t) + " v) {")
        self.out_cpp.inc_indent()
        self.out_cpp.println("m_" + self.field.name + " = v;")
        self.out_cpp.dec_indent()
        self.out_cpp.println("}")
                        
    def gen_string_accessors(self, t):
        # Generate a read-only accessor
        self.out_h.println(
            CppTypeNameGen(compressed=True,is_ref=True,is_const=True).gen(t) + 
            "get_" + self.field.name + "() const;")
        self.out_h.println()

        self.out_cpp.println(
            CppTypeNameGen(compressed=True,is_const=True,is_ref=True).gen(t) + 
                            self.clsname + "::get_" + self.field.name + "() const {")
        self.out_cpp.inc_indent()
        self.out_cpp.println("return m_" + self.field.name + ";")
        self.out_cpp.dec_indent()
        self.out_cpp.println("}")
        self.out_cpp.println()
        
        # Generate a setter
        self.out_h.println("void set_" + self.field.name + "(" +
            CppTypeNameGen(compressed=True,is_const=True,is_ref=True).gen(t) + "v);")

        self.out_cpp.println("void " + self.clsname + "::set_" + self.field.name + 
                "(" + CppTypeNameGen(compressed=True,is_const=True,is_ref=True).gen(t) + "v) {")
        self.out_cpp.inc_indent()
        self.out_cpp.println("m_" + self.field.name + " = v;")
        self.out_cpp.dec_indent()
        self.out_cpp.println("}")        
         
    def const_ref_ret(self, t):
        return CppTypeNameGen(compressed=True,is_ret=True,is_const=True).gen(t)
    
    def nonconst_ref_ret(self, t):
        return CppTypeNameGen(compressed=True,is_ret=True,is_const=False).gen(t)
    
    