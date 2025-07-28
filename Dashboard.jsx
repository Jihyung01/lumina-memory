import React, { useState, useEffect } from 'react';
import { 
  Calendar,
  Edit,
  TrendingUp,
  Heart,
  Brain,
  Target,
  Clock,
  CheckCircle,
  AlertCircle,
  MessageCircle,
  PlusCircle,
  ArrowRight,
  BarChart3,
  Smile,
  Frown,
  Meh
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { 
  dashboardAPI, 
  calendarAPI, 
  noteAPI, 
  coachingAPI,
  getErrorMessage 
} from '../api/apiService';
import AIAssistant from '../components/AIAssistant';

const Dashboard = () => {
  const navigate = useNavigate();
  
  // 상태 관리
  const [dashboardData, setDashboardData] = useState(null);
  const [todaySchedules, setTodaySchedules] = useState([]);
  const [upcomingSchedules, setUpcomingSchedules] = useState([]);
  const [recentNotes, setRecentNotes] = useState([]);
  const [coachingAdvice, setCoachingAdvice] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [coachingLoading, setCoachingLoading] = useState(false);

  // 데이터 로딩
  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // 병렬로 모든 데이터 로드
      const [dashboardRes, todayRes, upcomingRes, notesRes] = await Promise.all([
        dashboardAPI.getSummary(),
        calendarAPI.getTodaySchedules(),
        calendarAPI.getUpcomingSchedules(5),
        noteAPI.getNotes({ per_page: 5, sort: 'created_at', order: 'desc' })
      ]);

      if (dashboardRes.success) {
        setDashboardData(dashboardRes.data);
      }

      if (todayRes.success) {
        setTodaySchedules(todayRes.data.schedules || []);
      }

      if (upcomingRes.success) {
        setUpcomingSchedules(upcomingRes.data || []);
      }

      if (notesRes.success) {
        setRecentNotes(notesRes.data.notes || []);
      }

    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  // AI 코칭 요청
  const requestDailyCoaching = async () => {
    try {
      setCoachingLoading(true);
      const response = await coachingAPI.getDailySummary();
      
      if (response.success) {
        setCoachingAdvice(response.data);
      }
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setCoachingLoading(false);
    }
  };

  // 감정 아이콘 가져오기
  const getEmotionIcon = (emotionScore) => {
    if (emotionScore > 0.1) return <Smile className="w-5 h-5 text-green-500" />;
    if (emotionScore < -0.1) return <Frown className="w-5 h-5 text-red-500" />;
    return <Meh className="w-5 h-5 text-gray-500" />;
  };

  // 로딩 상태
  if (loading) {
    return (
      <div className="max-w-7xl mx-auto p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-300 rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-300 rounded"></div>
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-64 bg-gray-300 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-8">
      {/* 헤더 */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            안녕하세요! 👋
          </h1>
          <p className="text-gray-600 mt-1">
            오늘도 멋진 하루 되세요. 여기서 모든 것을 한눈에 확인하세요.
          </p>
        </div>

        <div className="flex gap-3">
          <button
            onClick={requestDailyCoaching}
            disabled={coachingLoading}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 flex items-center gap-2"
          >
            {coachingLoading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
            ) : (
              <Brain className="w-4 h-4" />
            )}
            일일 코칭
          </button>
          
          <button
            onClick={() => navigate('/notes')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <PlusCircle className="w-4 h-4" />
            새 메모
          </button>
        </div>
      </div>

      {/* 에러 메시지 */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700">{error}</p>
          <button 
            onClick={() => setError('')}
            className="mt-2 text-red-600 hover:text-red-800 text-sm underline"
          >
            닫기
          </button>
        </div>
      )}

      {/* 통계 카드 */}
      {dashboardData && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* 최근 메모 수 */}
          <div className="bg-white rounded-xl p-6 shadow-sm border hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">최근 7일 메모</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {dashboardData.overdue_count || 0}
                </p>
              </div>
              <div className="p-3 bg-orange-100 rounded-lg">
                <AlertCircle className="w-6 h-6 text-orange-600" />
              </div>
            </div>
            <p className="mt-4 text-orange-600 text-sm">
              {dashboardData.overdue_count > 0 ? '확인이 필요합니다' : '모두 완료!'}
            </p>
          </div>
        </div>
      )}

      {/* AI 코칭 결과 */}
      {coachingAdvice && (
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-6 border border-purple-200">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-purple-100 rounded-lg">
              <Brain className="w-6 h-6 text-purple-600" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                💜 오늘의 AI 코칭
              </h3>
              <div className="prose prose-sm max-w-none text-gray-700">
                <div className="whitespace-pre-wrap">{coachingAdvice.summary}</div>
              </div>
              <div className="flex items-center gap-4 mt-4 text-sm text-gray-500">
                <span>메모 {coachingAdvice.stats?.notes_count || 0}개</span>
                <span>일정 {coachingAdvice.stats?.schedules_count || 0}개 분석</span>
                <span>{new Date(coachingAdvice.generated_at).toLocaleTimeString('ko-KR', { 
                  hour: '2-digit', 
                  minute: '2-digit' 
                })}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 메인 콘텐츠 그리드 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 오늘의 일정 */}
        <div className="bg-white rounded-xl shadow-sm border">
          <div className="p-6 border-b border-gray-100">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <Calendar className="w-5 h-5 text-blue-600" />
                오늘의 일정
              </h3>
              <button
                onClick={() => navigate('/calendar')}
                className="text-blue-600 hover:text-blue-800 text-sm flex items-center gap-1"
              >
                모두 보기 <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
          
          <div className="p-6">
            {todaySchedules.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-4xl mb-2">🎉</div>
                <p className="text-gray-500">오늘은 일정이 없습니다!</p>
                <button
                  onClick={() => navigate('/calendar')}
                  className="mt-3 text-blue-600 hover:text-blue-800 text-sm"
                >
                  새 일정 만들기
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                {todaySchedules.slice(0, 4).map((schedule) => (
                  <div key={schedule.id} className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50">
                    <div className={`w-3 h-3 rounded-full mt-2 ${
                      schedule.is_completed ? 'bg-green-500' : 'bg-blue-500'
                    }`}></div>
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm font-medium ${
                        schedule.is_completed ? 'line-through text-gray-500' : 'text-gray-900'
                      }`}>
                        {schedule.title}
                      </p>
                      {schedule.start_time && (
                        <p className="text-xs text-gray-500 flex items-center gap-1 mt-1">
                          <Clock className="w-3 h-3" />
                          {schedule.start_time}
                          {schedule.end_time && ` - ${schedule.end_time}`}
                        </p>
                      )}
                    </div>
                    {schedule.is_completed ? (
                      <CheckCircle className="w-4 h-4 text-green-500 mt-1" />
                    ) : (
                      <div className="w-4 h-4 border-2 border-gray-300 rounded mt-1"></div>
                    )}
                  </div>
                ))}
                
                {todaySchedules.length > 4 && (
                  <div className="text-center pt-2">
                    <button
                      onClick={() => navigate('/calendar')}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      +{todaySchedules.length - 4}개 더 보기
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* 최근 메모 */}
        <div className="bg-white rounded-xl shadow-sm border">
          <div className="p-6 border-b border-gray-100">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <Edit className="w-5 h-5 text-green-600" />
                최근 메모
              </h3>
              <button
                onClick={() => navigate('/notes')}
                className="text-green-600 hover:text-green-800 text-sm flex items-center gap-1"
              >
                모두 보기 <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
          
          <div className="p-6">
            {recentNotes.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-4xl mb-2">📝</div>
                <p className="text-gray-500 mb-2">첫 메모를 작성해보세요!</p>
                <button
                  onClick={() => navigate('/notes')}
                  className="text-green-600 hover:text-green-800 text-sm"
                >
                  메모 작성하기
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {recentNotes.map((note) => (
                  <div key={note.id} className="p-3 rounded-lg hover:bg-gray-50 cursor-pointer"
                       onClick={() => navigate('/notes')}>
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-900 truncate">
                          {note.title}
                        </p>
                        <p className="text-sm text-gray-600 line-clamp-2 mt-1">
                          {note.content}
                        </p>
                        <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                          <span>{new Date(note.created_at).toLocaleDateString('ko-KR')}</span>
                          {note.emotion_label && (
                            <span className={`px-2 py-1 rounded flex items-center gap-1 ${
                              note.emotion_label === 'positive' ? 'bg-green-100 text-green-700' :
                              note.emotion_label === 'negative' ? 'bg-red-100 text-red-700' :
                              'bg-gray-100 text-gray-600'
                            }`}>
                              {note.emotion_label === 'positive' ? <Smile className="w-3 h-3" /> :
                               note.emotion_label === 'negative' ? <Frown className="w-3 h-3" /> :
                               <Meh className="w-3 h-3" />}
                              {note.emotion_label}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* 다가오는 일정 & 빠른 액션 */}
        <div className="space-y-6">
          {/* 다가오는 일정 */}
          <div className="bg-white rounded-xl shadow-sm border">
            <div className="p-6 border-b border-gray-100">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-purple-600" />
                다가오는 일정
              </h3>
            </div>
            
            <div className="p-6">
              {upcomingSchedules.length === 0 ? (
                <div className="text-center py-6">
                  <div className="text-3xl mb-2">⏰</div>
                  <p className="text-gray-500 text-sm">예정된 일정이 없습니다</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {upcomingSchedules.slice(0, 3).map((schedule) => (
                    <div key={schedule.id} className="flex items-center gap-3">
                      <div className="w-2 h-8 rounded-full" style={{backgroundColor: schedule.color}}></div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {schedule.title}
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(schedule.event_date).toLocaleDateString('ko-KR', {
                            month: 'short',
                            day: 'numeric',
                            weekday: 'short'
                          })}
                          {schedule.start_time && ` ${schedule.start_time}`}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* 빠른 액션 */}
          <div className="bg-white rounded-xl shadow-sm border">
            <div className="p-6 border-b border-gray-100">
              <h3 className="text-lg font-semibold text-gray-900">빠른 액션</h3>
            </div>
            
            <div className="p-6 space-y-3">
              <button
                onClick={() => navigate('/notes')}
                className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-blue-50 text-left transition-colors group"
              >
                <div className="p-2 bg-blue-100 rounded-lg group-hover:bg-blue-200">
                  <Edit className="w-4 h-4 text-blue-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">새 메모 작성</p>
                  <p className="text-xs text-gray-500">오늘의 생각을 기록하세요</p>
                </div>
              </button>
              
              <button
                onClick={() => navigate('/calendar')}
                className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-green-50 text-left transition-colors group"
              >
                <div className="p-2 bg-green-100 rounded-lg group-hover:bg-green-200">
                  <Calendar className="w-4 h-4 text-green-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">일정 추가</p>
                  <p className="text-xs text-gray-500">새로운 계획을 세워보세요</p>
                </div>
              </button>
              
              <button
                onClick={requestDailyCoaching}
                disabled={coachingLoading}
                className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-purple-50 text-left transition-colors group disabled:opacity-50"
              >
                <div className="p-2 bg-purple-100 rounded-lg group-hover:bg-purple-200">
                  {coachingLoading ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-purple-600 border-t-transparent" />
                  ) : (
                    <MessageCircle className="w-4 h-4 text-purple-600" />
                  )}
                </div>
                <div>
                  <p className="font-medium text-gray-900">AI 코칭 받기</p>
                  <p className="text-xs text-gray-500">개인화된 조언을 받아보세요</p>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 감정 트렌드 요약 (기본 데이터가 있는 경우) */}
      {dashboardData?.emotion_stats && dashboardData.emotion_stats.total_notes > 0 && (
        <div className="bg-white rounded-xl shadow-sm border">
          <div className="p-6 border-b border-gray-100">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-indigo-600" />
              감정 트렌드 요약
            </h3>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {dashboardData.emotion_stats.average_emotion.toFixed(2)}
                </div>
                <p className="text-sm text-gray-600">평균 감정 점수</p>
                <p className="text-xs text-gray-500 mt-1">
                  {dashboardData.emotion_stats.average_emotion > 0 ? '긍정적' : 
                   dashboardData.emotion_stats.average_emotion < 0 ? '부정적' : '중립적'} 상태
                </p>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {dashboardData.emotion_stats.total_notes}
                </div>
                <p className="text-sm text-gray-600">분석된 메모 수</p>
                <p className="text-xs text-gray-500 mt-1">최근 30일</p>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {dashboardData.emotion_stats.emotion_distribution ? 
                    Object.keys(dashboardData.emotion_stats.emotion_distribution)[0] || 'neutral'
                    : 'neutral'
                  }
                </div>
                <p className="text-sm text-gray-600">주요 감정 패턴</p>
                <p className="text-xs text-gray-500 mt-1">가장 빈번한 감정</p>
              </div>
            </div>
          </div>
        </div>
      )}return (
  <div className="max-w-7xl mx-auto p-6 space-y-8">
    {/* 기존 코드들... */}
    
    {/* AI 어시스턴트 추가 */}
    <AIAssistant 
      user={user} 
      notes={recentNotes} 
      schedules={[...todaySchedules, ...upcomingSchedules]} 
    />
  </div>
);
    </div>
    
  );
};

export default Dashboard;