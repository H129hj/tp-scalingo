import { FormEvent, useCallback, useEffect, useState } from "react";
import { Navigate, Route, Routes, useNavigate } from "react-router-dom";
import { Note, addNote, auth, deleteNote, listNotes } from "./api";

const TOKEN_KEY = "token";

function Login({ onToken }: { onToken: (t: string) => void }) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function submit(e: FormEvent) {
    e.preventDefault();
    try {
      const { access_token } = await auth(mode, email, password);
      onToken(access_token);
      navigate("/notes");
    } catch (err) {
      setError((err as Error).message);
    }
  }

  return (
    <form onSubmit={submit} style={{ maxWidth: 320, margin: "4rem auto", display: "grid", gap: 8 }}>
      <h1>{mode === "login" ? "Connexion" : "Creer un compte"}</h1>
      <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
      <input type="password" placeholder="Mot de passe (8 car. min)" minLength={8} value={password}
        onChange={(e) => setPassword(e.target.value)} required />
      <button type="submit">{mode === "login" ? "Se connecter" : "S'inscrire"}</button>
      <button type="button" onClick={() => setMode(mode === "login" ? "register" : "login")}>
        {mode === "login" ? "Pas de compte ? S'inscrire" : "Deja un compte ? Se connecter"}
      </button>
      {error && <p role="alert" style={{ color: "crimson" }}>{error}</p>}
    </form>
  );
}

function Notes({ token, onLogout }: { token: string; onLogout: () => void }) {
  const [notes, setNotes] = useState<Note[]>([]);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [error, setError] = useState("");

  const refresh = useCallback(
    () => listNotes(token).then(setNotes).catch((e: Error) => { setError(e.message); onLogout(); }),
    [token, onLogout],
  );
  useEffect(() => { refresh(); }, [refresh]);

  async function submit(e: FormEvent) {
    e.preventDefault();
    await addNote(token, title, body);
    setTitle(""); setBody("");
    refresh();
  }

  return (
    <main style={{ maxWidth: 560, margin: "2rem auto" }}>
      <button onClick={onLogout}>Deconnexion</button>
      <h1>Mes notes</h1>
      <form onSubmit={submit} style={{ display: "grid", gap: 8 }}>
        <input placeholder="Titre" value={title} onChange={(e) => setTitle(e.target.value)} required />
        <textarea placeholder="Contenu" value={body} onChange={(e) => setBody(e.target.value)} />
        <button type="submit">Ajouter</button>
      </form>
      {error && <p role="alert">{error}</p>}
      <ul>
        {notes.map((n) => (
          <li key={n.id}>
            <strong>{n.title}</strong> - {n.body}{" "}
            <button onClick={() => deleteNote(token, n.id).then(refresh)}>Supprimer</button>
          </li>
        ))}
      </ul>
    </main>
  );
}

export default function App() {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY));
  const save = (t: string) => { localStorage.setItem(TOKEN_KEY, t); setToken(t); };
  const logout = useCallback(() => { localStorage.removeItem(TOKEN_KEY); setToken(null); }, []);

  return (
    <Routes>
      <Route path="/" element={<Login onToken={save} />} />
      <Route path="/notes" element={token ? <Notes token={token} onLogout={logout} /> : <Navigate to="/" />} />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}
