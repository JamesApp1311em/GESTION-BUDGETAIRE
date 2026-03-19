import React, { useState } from "react";
import { ArrowUpRight, TrendingUp, CheckCircle2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

const mockData = {
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
  total: 1680,
  savings: 820,
  history: [
    { month: "Oct", income: 2400, total: 1850, savings: 550 },
    { month: "Nov", income: 2400, total: 1720, savings: 680 },
    { month: "Déc", income: 2500, total: 1950, savings: 550 },
    { month: "Jan", income: 2500, total: 1600, savings: 900 },
    { month: "Fév", income: 2500, total: 1750, savings: 750 },
    { month: "Mar", income: 2500, total: 1680, savings: 820 },
  ],
};

export default function ReportCard() {
  const [expenses, setExpenses] = useState(mockData.expenses);
  const [isSaving, setIsSaving] = useState(false);

  const handleExpenseChange = (key: keyof typeof mockData.expenses, value: string) => {
    const numValue = parseInt(value) || 0;
    setExpenses((prev) => ({ ...prev, [key]: numValue }));
  };

  const currentTotal = Object.values(expenses).reduce((a, b) => a + b, 0);
  const currentSavings = mockData.income - currentTotal;
  const savingsRate = ((currentSavings / mockData.income) * 100).toFixed(1);
  const isPositive = currentSavings > 0;

  const maxSavings = Math.max(...mockData.history.map((h) => h.savings), currentSavings);

  const handleSave = () => {
    setIsSaving(true);
    setTimeout(() => setIsSaving(false), 800);
  };

  return (
    <div className="min-h-screen bg-slate-50 p-4 md:p-8 flex items-center justify-center font-sans text-slate-800">
      <Card className="w-full max-w-2xl bg-white shadow-xl border-slate-200 overflow-hidden relative">
        {/* Header */}
        <div className="bg-slate-50 border-b border-slate-100 px-6 py-8 relative">
          <div className="absolute top-6 right-6 flex items-center gap-2">
            {isPositive && (
              <Badge variant="secondary" className="bg-emerald-100 text-emerald-800 hover:bg-emerald-100 border-0 flex items-center gap-1.5 px-3 py-1 text-xs font-medium">
                <CheckCircle2 className="w-3.5 h-3.5" />
                GOOD — {savingsRate}% épargnés
              </Badge>
            )}
          </div>
          
          <div className="mb-2 text-sm font-medium text-slate-500 uppercase tracking-wider">{mockData.user}</div>
          <h1 className="text-4xl font-bold text-slate-900 font-['Playfair_Display'] tracking-tight">
            Bilan Financier
          </h1>
          <p className="text-slate-500 mt-2">{mockData.month} {mockData.year}</p>
        </div>

        <CardContent className="p-0">
          {/* Chart Section */}
          <div className="px-6 py-8 border-b border-slate-100 bg-white">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wider">Progression des Épargnes</h3>
              <div className="flex items-center gap-1 text-sm font-medium text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full">
                <TrendingUp className="w-4 h-4" />
                <span>+9.3% vs Février</span>
              </div>
            </div>
            
            <div className="flex items-end justify-between h-40 gap-2 pb-2">
              {mockData.history.map((item, i) => {
                const isCurrentMonth = item.month === mockData.month;
                const barHeight = isCurrentMonth 
                  ? (currentSavings / maxSavings) * 100 
                  : (item.savings / maxSavings) * 100;
                  
                const displayValue = isCurrentMonth ? currentSavings : item.savings;

                return (
                  <div key={i} className="flex flex-col items-center flex-1 group">
                    <span className="text-xs font-medium text-slate-500 mb-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      ${displayValue}
                    </span>
                    <div className="w-full max-w-[40px] relative flex justify-center">
                      <div 
                        className={\`w-full rounded-t-sm transition-all duration-500 \${
                          isCurrentMonth ? "bg-blue-600 shadow-md" : "bg-slate-200"
                        }\`}
                        style={{ height: \`\${Math.max(barHeight, 5)}%\` }}
                      />
                    </div>
                    <span className={\`text-xs mt-3 font-medium \${isCurrentMonth ? "text-blue-700" : "text-slate-400"}\`}>
                      {item.month}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Mini Stat Cards */}
          <div className="grid grid-cols-3 divide-x divide-slate-100 border-b border-slate-100 bg-slate-50">
            <div className="p-6 text-center">
              <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Revenu</div>
              <div className="text-2xl font-bold text-slate-900">${mockData.income}</div>
            </div>
            <div className="p-6 text-center">
              <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Dépenses</div>
              <div className="text-2xl font-bold text-slate-900">${currentTotal}</div>
            </div>
            <div className="p-6 text-center">
              <div className="text-xs font-semibold text-emerald-600 uppercase tracking-wider mb-1">Épargne</div>
              <div className="text-2xl font-bold text-emerald-600">${currentSavings}</div>
            </div>
          </div>

          {/* Form Section */}
          <div className="p-6 md:p-8 bg-white">
            <h3 className="text-lg font-semibold text-slate-800 mb-6 font-['Playfair_Display']">
              Saisir les données — {mockData.month} {mockData.year}
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-5">
              <div className="space-y-2">
                <Label htmlFor="loyer" className="text-xs font-medium text-slate-500 uppercase">Loyer</Label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">$</span>
                  <Input 
                    id="loyer"
                    type="number" 
                    value={expenses.loyer}
                    onChange={(e) => handleExpenseChange("loyer", e.target.value)}
                    className="pl-7 bg-slate-50 border-slate-200 focus-visible:ring-blue-500"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="scolarite" className="text-xs font-medium text-slate-500 uppercase">Scolarité</Label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">$</span>
                  <Input 
                    id="scolarite"
                    type="number" 
                    value={expenses.scolarite}
                    onChange={(e) => handleExpenseChange("scolarite", e.target.value)}
                    className="pl-7 bg-slate-50 border-slate-200 focus-visible:ring-blue-500"
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="ration" className="text-xs font-medium text-slate-500 uppercase">Ration</Label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">$</span>
                  <Input 
                    id="ration"
                    type="number" 
                    value={expenses.ration}
                    onChange={(e) => handleExpenseChange("ration", e.target.value)}
                    className="pl-7 bg-slate-50 border-slate-200 focus-visible:ring-blue-500"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="dettes" className="text-xs font-medium text-slate-500 uppercase">Dettes</Label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">$</span>
                  <Input 
                    id="dettes"
                    type="number" 
                    value={expenses.dettes}
                    onChange={(e) => handleExpenseChange("dettes", e.target.value)}
                    className="pl-7 bg-slate-50 border-slate-200 focus-visible:ring-blue-500"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="poche" className="text-xs font-medium text-slate-500 uppercase">Poche</Label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">$</span>
                  <Input 
                    id="poche"
                    type="number" 
                    value={expenses.poche}
                    onChange={(e) => handleExpenseChange("poche", e.target.value)}
                    className="pl-7 bg-slate-50 border-slate-200 focus-visible:ring-blue-500"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="assistance" className="text-xs font-medium text-slate-500 uppercase">Assistance</Label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">$</span>
                  <Input 
                    id="assistance"
                    type="number" 
                    value={expenses.assistance}
                    onChange={(e) => handleExpenseChange("assistance", e.target.value)}
                    className="pl-7 bg-slate-50 border-slate-200 focus-visible:ring-blue-500"
                  />
                </div>
              </div>

              <div className="space-y-2 md:col-span-2 mt-2">
                <Label htmlFor="autres" className="text-xs font-medium text-slate-500 uppercase">Autres</Label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">$</span>
                  <Input 
                    id="autres"
                    type="number" 
                    value={expenses.autres}
                    onChange={(e) => handleExpenseChange("autres", e.target.value)}
                    className="pl-7 bg-slate-50 border-slate-200 focus-visible:ring-blue-500"
                  />
                </div>
              </div>
            </div>

            <div className="mt-8 pt-6 border-t border-slate-100 flex justify-end">
              <Button 
                onClick={handleSave} 
                disabled={isSaving}
                className="bg-blue-600 hover:bg-blue-700 text-white font-medium px-8 py-2.5 h-auto rounded-md shadow-sm transition-all"
              >
                {isSaving ? "Calcul en cours..." : "🚀 Calculer"}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
