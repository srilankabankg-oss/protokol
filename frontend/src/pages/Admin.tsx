import { useEffect, useState } from "react";
import { getOrganizations, createOrganization, getPeople, createPerson, getContracts, createContract, getUsers } from "../api/client";
import type { Organization, Person, Contract, User } from "../types";

const TABS = ["Организации", "Люди", "Договоры", "Пользователи"];

function Admin() {
  const [tab, setTab] = useState(0);
  const [orgs, setOrgs] = useState<Organization[]>([]);
  const [people, setPeople] = useState<Person[]>([]);
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<Record<string, string>>({});
  const [error, setError] = useState("");

  useEffect(() => { loadTab(tab); }, [tab]);

  async function loadTab(t: number) {
    setError("");
    try {
      if (t === 0) setOrgs(await getOrganizations());
      else if (t === 1) setPeople(await getPeople());
      else if (t === 2) setContracts(await getContracts());
      else setUsers(await getUsers());
    } catch { setError("Ошибка загрузки"); }
  }

  async function handleCreate() {
    setError("");
    try {
      if (tab === 0) await createOrganization({ name: form.name || "", inn: form.inn || "", profile: form.profile || "", role: form.role || "" });
      else if (tab === 1) await createPerson({ full_name: form.full_name || "", job_title: form.job_title || "", org_id: form.org_id || "" });
      else if (tab === 2) await createContract({ subject: form.subject || "", client_org_id: form.client_org_id || "", contractor_org_id: form.contractor_org_id || "", end_date: form.end_date || "" });
      setShowForm(false); setForm({}); loadTab(tab);
    } catch { setError("Ошибка создания"); }
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-1">Админ-панель</h1>
      <p className="text-gray-500 mb-6">Управление организациями, людьми, договорами и пользователями</p>
      <div className="flex gap-2 mb-6">
        {TABS.map((t, i) => (
          <button key={i} onClick={() => { setTab(i); setShowForm(false); }}
            className={"px-4 py-2 rounded-lg text-sm " + (tab === i ? "bg-blue-600 text-white" : "bg-white border text-gray-600")}
          >{t}</button>
        ))}
      </div>
      {error && <div className="bg-red-50 border border-red-200 p-3 text-sm text-red-700 rounded-lg mb-4">{error}</div>}
      <button onClick={() => setShowForm(!showForm)} className="mb-4 px-4 py-2 bg-green-600 text-white rounded-lg text-sm">+ Добавить</button>
      {showForm && (
        <div className="bg-white rounded-xl border p-6 mb-6 space-y-3">
          {tab === 0 && (<>
            <input placeholder="Название" className="w-full border rounded-lg px-3 py-2" onChange={e => setForm({...form, name: e.target.value})} />
            <input placeholder="ИНН" className="w-full border rounded-lg px-3 py-2" onChange={e => setForm({...form, inn: e.target.value})} />
            <textarea placeholder="Профиль организации" className="w-full border rounded-lg px-3 py-2" onChange={e => setForm({...form, profile: e.target.value})} />
            <select className="w-full border rounded-lg px-3 py-2" onChange={e => setForm({...form, role: e.target.value})}>
              <option value="">Роль организации</option>
              <option value="client">Заказчик</option>
              <option value="general_contractor">Генподрядчик</option>
              <option value="subcontractor">Субподрядчик</option>
              <option value="supplier">Поставщик</option>
            </select>
          </>)}
          {tab === 1 && (<>
            <input placeholder="ФИО" className="w-full border rounded-lg px-3 py-2" onChange={e => setForm({...form, full_name: e.target.value})} />
            <input placeholder="Должность" className="w-full border rounded-lg px-3 py-2" onChange={e => setForm({...form, job_title: e.target.value})} />
          </>)}
          {tab === 2 && (<>
            <input placeholder="Предмет договора" className="w-full border rounded-lg px-3 py-2" onChange={e => setForm({...form, subject: e.target.value})} />
            <input placeholder="ID заказчика" className="w-full border rounded-lg px-3 py-2" onChange={e => setForm({...form, client_org_id: e.target.value})} />
            <input placeholder="ID подрядчика" className="w-full border rounded-lg px-3 py-2" onChange={e => setForm({...form, contractor_org_id: e.target.value})} />
            <input type="date" className="w-full border rounded-lg px-3 py-2" onChange={e => setForm({...form, end_date: e.target.value})} />
          </>)}
          <div className="flex gap-2 pt-2">
            <button onClick={handleCreate} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm">Сохранить</button>
            <button onClick={() => setShowForm(false)} className="px-4 py-2 border rounded-lg text-sm">Отмена</button>
          </div>
        </div>
      )}
      <div className="space-y-2">
        {tab === 0 && orgs.map(o => <div key={o.id} className="bg-white rounded-lg border p-3 text-sm flex justify-between"><span>{o.name} {o.inn && "(ИНН: " + o.inn + ")"}</span><span className="text-gray-400">{o.role}</span></div>)}
        {tab === 1 && people.map(p => <div key={p.id} className="bg-white rounded-lg border p-3 text-sm">{p.full_name} {p.job_title && "— " + p.job_title}</div>)}
        {tab === 2 && contracts.map(c => <div key={c.id} className="bg-white rounded-lg border p-3 text-sm">{c.subject}</div>)}
        {tab === 3 && users.map(u => <div key={u.id} className="bg-white rounded-lg border p-3 text-sm flex justify-between"><span>{u.name} ({u.email})</span><span className="text-gray-400">{u.role}</span></div>)}
      </div>
    </div>
  );
}
export default Admin;