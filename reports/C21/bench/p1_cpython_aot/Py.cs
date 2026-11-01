using System.Runtime.InteropServices;

// Minimal CPython C API surface, bound with source-generated [LibraryImport] (AOT safe, no runtime marshalling stubs).
// Linux: libpython3.13.so.1.0. On Windows the same code would bind python313.dll.
internal static unsafe partial class Py
{
    const string Lib = "libpython3.13.so.1.0";
    public const int Py_file_input = 257;
    public const int PyBUF_READ = 0x100, PyBUF_WRITE = 0x200;

    [LibraryImport(Lib)] public static partial void Py_InitializeEx(int initsigs);
    [LibraryImport(Lib)] public static partial int Py_IsInitialized();
    [LibraryImport(Lib)] public static partial int Py_FinalizeEx();
    [LibraryImport(Lib, StringMarshalling = StringMarshalling.Utf8)] public static partial nint PyRun_StringFlags(string str, int start, nint globals, nint locals, nint flags);
    [LibraryImport(Lib, StringMarshalling = StringMarshalling.Utf8)] public static partial nint PyImport_AddModule(string name);
    [LibraryImport(Lib)] public static partial nint PyModule_GetDict(nint module);
    [LibraryImport(Lib, StringMarshalling = StringMarshalling.Utf8)] public static partial nint PyDict_GetItemString(nint dict, string key);
    [LibraryImport(Lib)] public static partial nint PyObject_CallNoArgs(nint callable);
    [LibraryImport(Lib)] public static partial nint PyObject_CallOneArg(nint callable, nint arg);
    [LibraryImport(Lib)] public static partial void Py_DecRef(nint o);
    [LibraryImport(Lib)] public static partial void Py_IncRef(nint o);
    [LibraryImport(Lib)] public static partial nint PyFloat_FromDouble(double v);
    [LibraryImport(Lib)] public static partial double PyFloat_AsDouble(nint o);
    [LibraryImport(Lib)] public static partial nint PyList_New(nint size);
    [LibraryImport(Lib)] public static partial int PyList_SetItem(nint list, nint i, nint item);
    [LibraryImport(Lib)] public static partial nint PyList_GetItem(nint list, nint i);
    [LibraryImport(Lib)] public static partial nint PyList_Size(nint list);
    [LibraryImport(Lib)] public static partial nint PyTuple_New(nint size);
    [LibraryImport(Lib)] public static partial int PyTuple_SetItem(nint t, nint i, nint item);
    [LibraryImport(Lib)] public static partial nint PyTuple_GetItem(nint t, nint i);
    [LibraryImport(Lib)] public static partial nint PyMemoryView_FromMemory(byte* mem, nint size, int flags);
    [LibraryImport(Lib)] public static partial nint PyErr_Occurred();
    [LibraryImport(Lib)] public static partial void PyErr_Print();
    [LibraryImport(Lib)] public static partial int PyGILState_Ensure();
    [LibraryImport(Lib)] public static partial void PyGILState_Release(int state);
    [LibraryImport(Lib)] public static partial nint PyEval_SaveThread();
    [LibraryImport(Lib)] public static partial void PyEval_RestoreThread(nint tstate);

    public const int RTLD_NOW = 2, RTLD_GLOBAL = 0x100;
    [LibraryImport("libc.so.6", StringMarshalling = StringMarshalling.Utf8)] public static partial nint dlopen(string file, int mode);

    public static nint Check(nint o, string what)
    {
        if (o == 0) { PyErr_Print(); throw new InvalidOperationException("Python error in " + what); }
        return o;
    }
}
