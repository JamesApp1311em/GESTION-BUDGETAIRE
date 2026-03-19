import React, { useState, useMemo } from "react";
import { Save, Printer, ArrowUpRight, ArrowDownRight, CheckCircle2, AlertTriangle } from "lucide-react";

interface Expenses {
  loyer: number;
  scolarite: number;
  ration: number;
  dettes: number;
  poche: number;
  assistance: number;
  autres: number;
}

const CATEGORY_LABELS: Record<keyof Expenses, string> = {
  loyer: "Loyer",
  scolarite: "Scolarité",
  ration: "Ration",
  dettes: "Dettes",
  poche: "Poche",
  assistance: "Assistance",
  autres: "Autres",
};

const CATEGORY_COLORS: Record<keyof Expenses, string> = {
  loyer: "bg-blue-500",
  scolarite: "bg-indigo-500",
  ration: "bg-violet-500",
  dettes: "bg-purple-500",
  poche: "bg-fuchsia-500",
  assistance: "bg-pink-500",
  autres: "bg-rose-500",
};

const INITIAL_DATA = {
  user: "Jean Martin",
  month: "Mars",
  year: "2026",
  income: 2500,
  expenses: {
    loyer: 650,
    scolarite: 180,
    ration: 320,
    dettes: 200,
    poche: 100,
    assistance: 150,
    autres: 80,
  },
};

export default function Cockpit() {
  const [income, setIncome] = useState(INITIAL_DATA.income);
  const [expenses, setExpenses] = useState<Expenses>(INITIAL_DATA.expenses);

  const totalExpenses = useMemo(() => {
    return Object.values(expenses).reduce((acc, val) => acc + (Number(val) || 0), 0);
  }, [expenses]);

  const savings = income - totalExpenses;
  const savingsRate = income > 0 ? (savings / income) * 100 : 0;
  const isPositive = savings >= 0;

  const handleExpenseChange = (key: keyof Expenses, value: string) => {
    const numValue = value === "" ? 0 : Number(value);
    setExpenses((prev) => ({ ...prev, [key]: numValue }));
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 font-sans selection:bg-blue-500/30">
      <div className="max-w-[500px] mx-auto p-6 flex flex-col gap-6">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div>
            <h1 className="text-xl font-semibold tracking-tight text-white flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div>
              Tableau de Bord
            </h1>
            <p className="text-slate-400 text-sm">{INITIAL_DATA.month} {INITIAL_DATA.year} • {INITIAL_DATA.user}</p>
          </div>
          <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border ${isPositive ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'}`}>
            {isPositive ? <CheckCircle2 className="w-3.5 h-3.5" /> : <AlertTriangle className="w-3.5 h-3.5" />}
            {isPositive ? 'GOOD ✓' : 'ATTENTION'}
          </div>
        </div>

        {/* Metrics Row */}
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col justify-between">
            <span className="text-slate-400 text-xs font-medium uppercase tracking-wider">Revenu Total</span>
            <div className="flex items-baseline gap-1 mt-2">
              <span className="text-xl font-bold text-white">${income.toLocaleString()}</span>
            </div>
          </div>
          
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col justify-between">
            <span className="text-slate-400 text-xs font-medium uppercase tracking-wider">Total Dépenses</span>
            <div className="flex items-baseline gap-1 mt-2">
              <span className="text-xl font-bold text-white">${totalExpenses.toLocaleString()}</span>
            </div>
          </div>

          <div className={`border rounded-xl p-4 flex flex-col justify-between relative overflow-hidden ${isPositive ? 'bg-emerald-950/30 border-emerald-500/30' : 'bg-red-950/30 border-red-500/30'}`}>
            <div className="absolute top-0 right-0 p-2 opacity-10">
              {isPositive ? <ArrowUpRight className="w-16 h-16" /> : <ArrowDownRight className="w-16 h-16" />}
            </div>
            <div className="flex flex-col relative z-10">
              <span className={`text-xs font-medium uppercase tracking-wider ${isPositive ? 'text-emerald-400/80' : 'text-red-400/80'}`}>Épargne Nette</span>
              <div className="flex items-center gap-1 mt-2">
                <span className={`text-xl font-bold ${isPositive ? 'text-emerald-400' : 'text-red-400'}`}>
                  ${Math.abs(savings).toLocaleString()}
                </span>
                {isPositive ? <ArrowUpRight className="w-4 h-4 text-emerald-500" /> : <ArrowDownRight className="w-4 h-4 text-red-500" />}
              </div>
            </div>
          </div>
        </div>

        {/* Savings Rate Large Display */}
        <div className="flex justify-center items-center py-4 border-b border-slate-800/50">
           <div className="text-center">
             <div className="text-slate-400 text-sm font-medium uppercase tracking-widest mb-1">Taux d'Épargne</div>
             <div className={`text-5xl font-light tracking-tighter ${isPositive ? 'text-emerald-400' : 'text-red-400'}`}>
               {savingsRate.toFixed(1)}%
             </div>
           </div>
        </div>

        {/* Allocation Bar */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col gap-4">
          <div className="flex justify-between items-center">
            <h2 className="text-sm font-medium text-slate-300">Allocation des Dépenses</h2>
            <span className="text-xs text-slate-500">{(totalExpenses / income * 100).toFixed(1)}% du revenu</span>
          </div>
          
          <div className="h-4 w-full bg-slate-950 rounded-full overflow-hidden flex ring-1 ring-slate-800">
            {Object.entries(expenses).map(([key, value]) => {
              const width = totalExpenses > 0 ? ((value as number) / totalExpenses) * 100 : 0;
              if (width === 0) return null;
              return (
                <div 
                  key={key} 
                  className={`h-full ${CATEGORY_COLORS[key as keyof Expenses]} transition-all duration-300 border-r border-slate-900 last:border-0`}
                  style={{ width: `${width}%` }}
                  title={`${CATEGORY_LABELS[key as keyof Expenses]}: ${value}$`}
                />
              );
            })}
          </div>

          <div className="flex flex-wrap gap-x-4 gap-y-2 mt-1">
            {Object.entries(expenses).map(([key, value]) => {
              if (!value) return null;
              const percentage = totalExpenses > 0 ? ((value as number) / totalExpenses) * 100 : 0;
              return (
                <div key={key} className="flex items-center gap-1.5">
                  <div className={`w-2 h-2 rounded-full ${CATEGORY_COLORS[key as keyof Expenses]}`} />
                  <span className="text-xs text-slate-400">{CATEGORY_LABELS[key as keyof Expenses]}</span>
                  <span className="text-xs font-medium text-slate-300">{percentage.toFixed(0)}%</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Input Grid */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col gap-4">
          <h2 className="text-sm font-medium text-slate-300">Saisie Rapide</h2>
          
          <div className="grid grid-cols-2 gap-x-4 gap-y-3">
            {Object.entries(CATEGORY_LABELS).map(([key, label]) => (
              <div key={key} className="flex flex-col gap-1.5">
                <label htmlFor={key} className="text-xs text-slate-400 font-medium">
                  {label}
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 text-sm">$</span>
                  <input
                    type="number"
                    id={key}
                    value={expenses[key as keyof Expenses] || ""}
                    onChange={(e) => handleExpenseChange(key as keyof Expenses, e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2 pl-7 pr-3 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition-colors placeholder:text-slate-700"
                    placeholder="0"
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3 pt-2">
          <button className="flex-1 bg-blue-600 hover:bg-blue-500 text-white font-medium py-3 rounded-xl flex items-center justify-center gap-2 transition-colors shadow-lg shadow-blue-500/20">
            <Save className="w-4 h-4" />
            Sauvegarder
          </button>
          <button className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium py-3 rounded-xl flex items-center justify-center gap-2 transition-colors border border-slate-700">
            <Printer className="w-4 h-4" />
            Imprimer PDF
          </button>
        </div>

      </div>
    </div>
  );
}
